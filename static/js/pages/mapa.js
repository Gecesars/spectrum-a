const OVERLAY_DEFAULT_OPACITY = 0.85;

const state = {
    map: null,
    txMarker: null,
    txData: null,
    txCoords: null,
    rxEntries: [],
    selectedRxIndex: null,
    linkLine: null,
    coverageOverlay: null,
    radiusCircle: null,
    coverageData: null,
    overlayOpacity: OVERLAY_DEFAULT_OPACITY,
    elevationService: null,
    pendingTiltTimeout: null,
};

function formatNumber(value, suffix = '') {
    if (value === undefined || value === null || Number.isNaN(value)) {
        return '-';
    }
    return `${Number(value).toFixed(2)}${suffix}`;
}

function formatDb(value) {
    if (value === undefined || value === null || Number.isNaN(value)) {
        return '-';
    }
    return `${Number(value).toFixed(2)} dB`;
}

function updateRadiusLabel() {
    const radiusInput = document.getElementById('radiusInput');
    const radiusValue = document.getElementById('radiusValue');
    radiusValue.textContent = `${radiusInput.value} km`;
}

function updateTiltLabel(value) {
    document.getElementById('tiltValue').textContent = `${Number(value).toFixed(1)}°`;
}

function updateTxSummary(data) {
    document.getElementById('txLat').textContent = formatNumber(data.latitude, '°');
    document.getElementById('txLng').textContent = formatNumber(data.longitude, '°');
    document.getElementById('txFreq').textContent = data.frequency ? `${Number(data.frequency).toFixed(2)} MHz` : '-';
    document.getElementById('txModel').textContent = data.propagationModel || '-';
    updateTiltLabel(data.antennaTilt || 0);
    document.getElementById('tiltControl').value = data.antennaTilt ?? 0;
}

function updateGainSummary(gainComponents, scale) {
    if (!gainComponents) {
        document.getElementById('gainBase').textContent = '-';
        document.getElementById('gainHorizontal').textContent = '-';
        document.getElementById('gainVertical').textContent = '-';
        document.getElementById('fieldScale').textContent = '-';
        return;
    }
    document.getElementById('gainBase').textContent = formatDb(gainComponents.base_gain_dbi || 0);
    if (gainComponents.horizontal_adjustment_db_min !== undefined) {
        const min = formatDb(gainComponents.horizontal_adjustment_db_min);
        const max = formatDb(gainComponents.horizontal_adjustment_db_max);
        document.getElementById('gainHorizontal').textContent = `${min} / ${max}`;
    }
    document.getElementById('gainVertical').textContent = formatDb(gainComponents.vertical_adjustment_db);
    if (scale) {
        document.getElementById('fieldScale').textContent = `${formatNumber(scale.min)} – ${formatNumber(scale.max)} dBµV/m`;
    }
}

function showToast(message, isError = false) {
    const card = document.getElementById('mapTooltip');
    if (!card) return;
    card.innerHTML = `<h4>${isError ? 'Atenção' : 'Cobertura'}</h4><p>${message}</p>`;
    card.hidden = false;
    setTimeout(() => {
        card.hidden = true;
    }, 3600);
}

function ensureElevationService() {
    if (!state.elevationService) {
        state.elevationService = new google.maps.ElevationService();
    }
    return state.elevationService;
}

function clearCoverageOverlay() {
    if (state.coverageOverlay) {
        state.coverageOverlay.setMap(null);
        state.coverageOverlay = null;
    }
    if (state.radiusCircle) {
        state.radiusCircle.setMap(null);
        state.radiusCircle = null;
    }
}

function applyCoverageOverlay(response) {
    clearCoverageOverlay();
    const bounds = response.bounds;
    if (!bounds || !state.map) return;

    const overlayBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(bounds.south, bounds.west),
        new google.maps.LatLng(bounds.north, bounds.east)
    );

    const overlay = new google.maps.GroundOverlay(
        `data:image/png;base64,${response.image}`,
        overlayBounds,
        { opacity: state.overlayOpacity }
    );
    overlay.setMap(state.map);
    state.coverageOverlay = overlay;

    if (response.colorbar) {
        const card = document.getElementById('colorbarCard');
        const img = document.getElementById('colorbarImage');
        img.src = `data:image/png;base64,${response.colorbar}`;
        card.hidden = false;
    }

    if (response.requested_radius_km && response.center) {
        const centerLatLng = new google.maps.LatLng(response.center.lat, response.center.lng);
        state.radiusCircle = new google.maps.Circle({
            map: state.map,
            center: centerLatLng,
            radius: response.requested_radius_km * 1000,
            strokeColor: '#0d6efd',
            strokeOpacity: 0.4,
            strokeWeight: 2,
            fillColor: '#0d6efd',
            fillOpacity: 0.1,
        });
    }
}

function setOverlayOpacity(value) {
    state.overlayOpacity = value;
    if (state.coverageOverlay) {
        state.coverageOverlay.setOpacity(value);
    }
    if (state.radiusCircle) {
        state.radiusCircle.setOptions({ fillOpacity: Math.max(0.05, value / 6) });
    }
}

function findNearestFieldStrength(lat, lng, dict) {
    let best = null;
    let bestDist = Infinity;
    Object.entries(dict).forEach(([key, value]) => {
        const [lt, ln] = key.slice(1, -1).split(',').map(Number);
        const dist = Math.hypot(lat - lt, lng - ln);
        if (dist < bestDist) {
            bestDist = dist;
            best = value;
        }
    });
    return best;
}

function updateLinkSummary(summary) {
    document.getElementById('linkDistance').textContent = summary.distance || '-';
    document.getElementById('linkBearing').textContent = summary.bearing || '-';
    document.getElementById('linkField').textContent = summary.field || '-';
    document.getElementById('linkElevation').textContent = summary.elevation || '-';
}

function highlightRxEntry(index) {
    state.rxEntries.forEach((entry, idx) => {
        entry.marker.setIcon(idx === index ? entry.icons.selected : entry.icons.default);
    });
}

function updateLinkVisuals(entry) {
    if (state.linkLine) {
        state.linkLine.setMap(null);
    }
    state.linkLine = new google.maps.Polyline({
        map: state.map,
        path: [state.txCoords, entry.marker.getPosition()],
        strokeColor: '#0d6efd',
        strokeOpacity: 0.9,
        strokeWeight: 3,
    });
    if (entry.summary) {
        updateLinkSummary(entry.summary);
    }
}

function selectRx(index) {
    state.selectedRxIndex = index;
    highlightRxEntry(index);
    const entry = state.rxEntries[index];
    updateLinkVisuals(entry);
    document.getElementById('btnGenerateProfile').disabled = false;
}

function removeRx(index) {
    const [entry] = state.rxEntries.splice(index, 1);
    if (entry) {
        entry.marker.setMap(null);
    }
    if (state.linkLine) {
        state.linkLine.setMap(null);
        state.linkLine = null;
    }
    state.selectedRxIndex = null;
    updateLinkSummary({});
    renderRxList();
}

function clearReceivers() {
    state.rxEntries.forEach((entry) => entry.marker.setMap(null));
    state.rxEntries = [];
    state.selectedRxIndex = null;
    if (state.linkLine) {
        state.linkLine.setMap(null);
        state.linkLine = null;
    }
    updateLinkSummary({});
    renderRxList();
    document.getElementById('btnGenerateProfile').disabled = true;
}

function renderRxList() {
    const container = document.getElementById('rxList');
    container.innerHTML = '';
    if (!state.rxEntries.length) {
        container.innerHTML = '<li class="rx-empty">Nenhum ponto RX selecionado.</li>';
        return;
    }

    state.rxEntries.forEach((entry, idx) => {
        const li = document.createElement('li');
        li.className = `rx-item${idx === state.selectedRxIndex ? ' selected' : ''}`;
        const title = document.createElement('div');
        title.className = 'rx-title';
        title.textContent = `RX ${idx + 1}`;

        const details = document.createElement('div');
        details.className = 'rx-details';
        const summary = entry.summary || {};
        details.innerHTML = `
            <span>${summary.distance || '-'}</span>
            <span>${summary.field || '-'}</span>
            <span>${summary.elevation || '-'}</span>
        `;

        const actions = document.createElement('div');
        actions.className = 'rx-actions';
        const focusBtn = document.createElement('button');
        focusBtn.type = 'button';
        focusBtn.textContent = 'Focar';
        focusBtn.className = 'btn btn-sm btn-outline-primary';
        focusBtn.onclick = () => {
            state.map.panTo(entry.marker.getPosition());
            state.map.setZoom(Math.max(state.map.getZoom(), 11));
            selectRx(idx);
        };

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.textContent = 'Remover';
        removeBtn.className = 'btn btn-sm btn-link text-danger';
        removeBtn.onclick = () => removeRx(idx);

        actions.appendChild(focusBtn);
        actions.appendChild(removeBtn);

        li.appendChild(title);
        li.appendChild(details);
        li.appendChild(actions);
        li.onclick = (event) => {
            if (event.target === removeBtn || event.target === focusBtn) return;
            selectRx(idx);
        };
        container.appendChild(li);
    });
}

function getElevation(position) {
    ensureElevationService();
    return new Promise((resolve) => {
        state.elevationService.getElevationForLocations({ locations: [position] }, (results, status) => {
            if (status === 'OK' && results && results.length) {
                resolve(results[0].elevation);
            } else {
                resolve(null);
            }
        });
    });
}

function computeReceiverSummary(position) {
    const distanceMeters = google.maps.geometry.spherical.computeDistanceBetween(state.txCoords, position);
    const bearing = google.maps.geometry.spherical.computeHeading(state.txCoords, position);
    const summary = {
        distance: `${(distanceMeters / 1000).toFixed(2)} km`,
        bearing: `${bearing.toFixed(1)}°`,
    };

    if (state.coverageData && state.coverageData.signal_level_dict) {
        const field = findNearestFieldStrength(position.lat(), position.lng(), state.coverageData.signal_level_dict);
        if (field !== null) {
            summary.field = `${field.toFixed(1)} dBµV/m`;
        }
    }

    return getElevation(position).then((elevation) => {
        if (elevation !== null) {
            summary.elevation = `${elevation.toFixed(1)} m`;
        }
        return summary;
    });
}

function createRxMarker(position) {
    const defaultIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: '#6610f2',
        fillOpacity: 0.85,
        scale: 7,
        strokeColor: '#fff',
        strokeWeight: 2,
    };
    const selectedIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillColor: '#d63384',
        fillOpacity: 1,
        scale: 8,
        strokeColor: '#fff',
        strokeWeight: 2,
    };

    const marker = new google.maps.Marker({
        position,
        map: state.map,
        icon: defaultIcon,
        title: `RX ${state.rxEntries.length + 1}`,
    });

    const entry = {
        marker,
        summary: null,
        icons: { default: defaultIcon, selected: selectedIcon },
    };

    marker.addListener('click', () => {
        const index = state.rxEntries.indexOf(entry);
        if (index >= 0) {
            selectRx(index);
        }
    });

    state.rxEntries.push(entry);
    computeReceiverSummary(position).then((summary) => {
        entry.summary = summary;
        if (state.selectedRxIndex === state.rxEntries.indexOf(entry)) {
            updateLinkSummary(summary);
        }
        renderRxList();
    });
    renderRxList();
    selectRx(state.rxEntries.length - 1);
}

function handleMapClick(event) {
    if (!state.txCoords) return;
    createRxMarker(event.latLng);
}

function setTxCoords(latLng, { pan = false } = {}) {
    state.txCoords = latLng;
    if (state.txMarker) {
        state.txMarker.setPosition(latLng);
    }
    if (pan) {
        state.map.panTo(latLng);
    }
    if (state.txData) {
        state.txData.latitude = latLng.lat();
        state.txData.longitude = latLng.lng();
        updateTxSummary(state.txData);
    }
    state.rxEntries.forEach((entry, idx) => {
        if (entry.summary) {
            computeReceiverSummary(entry.marker.getPosition()).then((summary) => {
                entry.summary = summary;
                if (idx === state.selectedRxIndex) {
                    updateLinkSummary(summary);
                }
                renderRxList();
            });
        }
    });
}

function handleTxDragEnd(event) {
    const position = event.latLng;
    setTxCoords(position, { pan: false });
    showToast('Posição da TX atualizada. Gere a cobertura novamente.', false);
}

function saveTilt(value) {
    if (state.pendingTiltTimeout) {
        clearTimeout(state.pendingTiltTimeout);
    }
    state.pendingTiltTimeout = setTimeout(() => {
        fetch('/update-tilt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tilt: value }),
        }).then((response) => {
            if (!response.ok) {
                throw new Error('Falha ao atualizar tilt');
            }
            return response.json();
        }).then(() => {
            if (state.txData) {
                state.txData.antennaTilt = Number(value);
            }
            showToast('Tilt atualizado');
        }).catch((error) => {
            console.error(error);
            showToast('Erro ao atualizar tilt', true);
        });
    }, 350);
}

function generateCoverage() {
    if (!state.txCoords) return;
    const radiusKm = Number(document.getElementById('radiusInput').value) || 0;
    const minField = document.getElementById('minField').value;
    const maxField = document.getElementById('maxField').value;

    const payload = {
        radius: radiusKm,
        minSignalLevel: minField || null,
        maxSignalLevel: maxField || null,
        customCenter: { lat: state.txCoords.lat(), lng: state.txCoords.lng() },
    };

    fetch('/calculate-coverage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    }).then((response) => {
        if (!response.ok) {
            throw new Error('Falha ao gerar cobertura');
        }
        return response.json();
    }).then((data) => {
        state.coverageData = data;
        if (data.center) {
            const centerLatLng = new google.maps.LatLng(data.center.lat, data.center.lng);
            setTxCoords(centerLatLng, { pan: false });
        }
        applyCoverageOverlay(data);
        updateGainSummary(data.gain_components, data.scale);
        showToast('Cobertura atualizada com sucesso');
    }).catch((error) => {
        console.error(error);
        showToast('Não foi possível gerar a cobertura', true);
    });
}

function generateProfile() {
    if (state.selectedRxIndex === null) {
        showToast('Selecione um RX na lista', true);
        return;
    }
    const entry = state.rxEntries[state.selectedRxIndex];
    if (!entry || !state.txCoords) return;

    const tx = state.txCoords;
    const rx = entry.marker.getPosition();
    const payload = {
        path: [
            { lat: tx.lat(), lng: tx.lng() },
            { lat: rx.lat(), lng: rx.lng() },
        ],
    };

    fetch('/gerar_img_perfil', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    }).then((response) => {
        if (!response.ok) {
            throw new Error('Falha ao gerar perfil');
        }
        return response.json();
    }).then((data) => {
        const img = document.getElementById('profileImage');
        img.src = `data:image/png;base64,${data.image}`;
        const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('profileModal'));
        modal.show();
    }).catch((error) => {
        console.error(error);
        showToast('Não foi possível gerar o perfil', true);
    });
}

function initControls() {
    document.getElementById('radiusInput').addEventListener('input', updateRadiusLabel);
    document.getElementById('btnGenerateCoverage').addEventListener('click', generateCoverage);
    document.getElementById('btnGenerateProfile').addEventListener('click', generateProfile);
    document.getElementById('btnClearRx').addEventListener('click', clearReceivers);

    const overlayInput = document.getElementById('overlayOpacity');
    const overlayLabel = document.getElementById('overlayOpacityValue');
    overlayInput.addEventListener('input', (event) => {
        const value = Number(event.target.value);
        overlayLabel.textContent = value.toFixed(2);
        setOverlayOpacity(value);
    });
    overlayInput.value = OVERLAY_DEFAULT_OPACITY;
    overlayLabel.textContent = OVERLAY_DEFAULT_OPACITY.toFixed(2);

    const tiltControl = document.getElementById('tiltControl');
    tiltControl.addEventListener('input', (event) => {
        updateTiltLabel(event.target.value);
    });
    tiltControl.addEventListener('change', (event) => {
        saveTilt(event.target.value);
    });

    updateRadiusLabel();
}

function initCoverageMap() {
    fetch('/carregar-dados')
        .then((response) => response.json())
        .then((data) => {
            state.txData = { ...data };
            const txLatLng = new google.maps.LatLng(data.latitude, data.longitude);
            state.txCoords = txLatLng;
            updateTxSummary(data);

            state.map = new google.maps.Map(document.getElementById('coverageMap'), {
                center: txLatLng,
                zoom: 9,
                mapTypeId: 'terrain',
                gestureHandling: 'greedy',
            });

            state.txMarker = new google.maps.Marker({
                position: txLatLng,
                map: state.map,
                title: 'Transmissor',
                draggable: true,
                icon: {
                    url: 'https://maps.gstatic.com/mapfiles/ms2/micons/red-dot.png',
                },
            });
            state.txMarker.addListener('dragend', handleTxDragEnd);

            state.map.addListener('click', handleMapClick);

            initControls();
            ensureElevationService();
        })
        .catch((error) => {
            console.error('Erro ao carregar dados do usuário', error);
            showToast('Não foi possível carregar os dados iniciais', true);
        });
}

window.initCoverageMap = initCoverageMap;
