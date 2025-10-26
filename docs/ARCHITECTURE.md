# ATX Coverage – Visão Geral da Arquitetura (v2)

## Estrutura do backend

- `app_core/__init__.py` concentra a fábrica da aplicação Flask. Lá são feitas:
  - leitura de configurações (secret, banco de dados, Google Maps, diretório de assets),
  - inicialização de extensões (`SQLAlchemy`, `LoginManager`, `Flask-Migrate`, `CORS`),
  - registro do *blueprint* principal (`app_core.routes.ui.bp`),
  - injeção de variáveis globais de template (ex.: `current_year`).
- `app_core/routes/ui.py` contém todo o conjunto de rotas e utilidades utilizadas na aplicação:
  - rotas públicas (landing, login/registro),
  - rotas autenticadas (dashboard, antena, cobertura, relatório, dados salvos),
  - serviços REST que manipulam diagramas, notas, perfis, relatórios, cálculos de cobertura e perfil de terreno,
  - funções auxiliares para parsing de arquivos `.pat`, cálculos matemáticos (pycraf/astropy) e geração de gráficos.
- `extensions.py` e `user.py` continuam expondo as instâncias compartilhadas (`db`, `login_manager`, modelo `User`).
- `app3.py` passa a ser apenas o ponto de entrada: importa `create_app`, aplica pequenas configurações de runtime (`OMP`/`OPENBLAS`) e executa `app.run` quando chamado diretamente. O objetivo é manter compatibilidade com `Procfile`/`gunicorn`.

## Organização de templates e assets

- `templates/layouts/base.html` fornece o *layout shell* padrão (header, navegação, footer, toasts). Todos os templates agora usam `{% extends %}`.
- CSS global em `static/css/main.css`; estilos específicos em `static/css/pages/<page>.css`.
- Scripts compartilhados padrão em `static/js/main.js`; lógica de página em `static/js/pages/<page>.js`.
- Páginas reconstruídas:
  - `templates/index.html`, `register.html`, `home.html`, `inicio.html` – usam o layout e os novos estilos consistentes.
  - `templates/calcular_cobertura.html` – interface reorganizada, modais compatíveis com Bootstrap 5, assets externos extraídos.
  - `templates/antena.html` – sidebar fixa para ajustes, pre-visualização responsiva dos diagramas.
- Assets pesados (PDFs, imagens técnicas) permanecem em `static/`, mas agora o UI consome apenas imagens otimizadas para preview.

## Fluxos principais

1. **Autenticação**  
   - Login/registro via `ui.login`/`ui.register`.  
   - `LoginManager` redireciona automaticamente para `ui.login` quando necessário.
2. **Dashboard (home)**  
   - Ações rápidas para sensores, cobertura, cálculos RF e mapas.  
   - Notas salvas assíncronas via `/update-notes`.
3. **Antena**  
   - Upload e pré-visualização dos diagramas `.pat`.  
   - Ajustes de direção/tilt fazem POST para `/upload_diagrama`; persistência via `/salvar_diagrama`.
4. **Cobertura**  
   - Formulário segmentado (posicionamento, propagação, especificações).  
   - Coordenadas por mapa Google ou entrada manual; salvamento em `/salvar-dados`.  
   - Botões direcionam para visualização (`/mapa`) e dados históricos (`/visualizar-dados-salvos`).
5. **Relatórios e perfis**  
   - Geração de PDF (`/gerar-relatorio`), perfil com curvatura (`/gerar_img_perfil`) e mapas de cobertura (`/calculate-coverage`) permanecem com a mesma lógica científica existente.

## Próximos passos recomendados

1. **Cobertura / mapa**  
   - Criar feedback visual ao gerar cobertura (loading + apresentação do mapa diretamente nesta página).
   - Extrair parâmetros avançados (raio, níveis mínimo/máximo) para o formulário – hoje estão hard-coded.
2. **Antena**  
   - Exibir dados numéricos (HPBW, diretividade) ao lado dos gráficos, reaproveitando o JSON salvo no usuário.
   - Disponibilizar histórico de arquivos `.pat` por usuário.
3. **Arquitetura**  
   - Continuar modularização dividindo `app_core/routes/ui.py` em *blueprints* menores (ex.: `auth`, `antenna`, `coverage`, `reports`).
   - Extrair helpers de cálculo para `app_core/services/` com testes unitários.
4. **Front-end**  
   - Centralizar componentes (botões, cards, toasts) em um *design system* leve para evitar duplicidade de estilos no futuro.
   - Incluir testes e lint para JS/CSS (por exemplo com `eslint`/`stylelint`).

Este documento deve servir como guia rápido da versão atual e como referência dos próximos incrementos planejados.
