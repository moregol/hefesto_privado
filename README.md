# Hefesto — Simulação do foguete IREC

Simulação de voo do foguete Hefesto para a IREC. Combina:
- **OpenMotor** (balística interna do motor via `.ric`)
- **RocketPy** (dinâmica de voo com atmosfera ERA5)
- **RASAero** (arrasto aerodinâmico via `.csv`)

Consulte o [GLOSSARY.md](file:///home/icaro/Hub/01-Projetos_e_UFJF/supernova/simulacoes/github/hefesto%20privado-estrutura-vibe/GLOSSARY.md) para as definições canônicas de termos, referenciais de coordenadas e convenção de momentos de inércia `(I_11, I_22, I_33) = (I_transversal, I_transversal, I_longitudinal)`.
## Downloads Necessários
Para o funcionamento do CPython é necessario baixar o Build Tools da Microsoft para C++, [Esse](https://stackoverflow.com/questions/40504552/how-to-install-visual-c-build-tools) site é um tutorial para a instalação do tools, após isso apenas rode o setup.bat antes de rodar o codigo pelo vscode e o projeto estará funcionando. Caso a extensão apresente erros é necessario limpar o cache do vscode, provavelmente o erro aparecido é o mesmo [dessa](https://stackoverflow.com/questions/67698176/error-loading-webview-error-could-not-register-service-workers-typeerror-fai) thread ensinando como voce pode resolver o erro.
## Arquitetura e Direção de Dependências

O projeto segue um fluxo **estritamente unidirecional**:
`centralControle/ & scripts/` → `configs/` → `src/`

- **`src/` nunca importa `configs/`**: toda função de `src/` recebe suas especificações (`Specs`) explicitamente por argumento.
- **`configs/` possui zero I/O no `import`**: declara apenas objetos imutáveis (`MotorSpec`, `FogueteSpec`, `TuboSpec`, `AletaSpec`, `CoifaSpec`); a leitura de arquivos `.ric`/`.eng` acontece apenas sob demanda dentro de `derivar_motor()`.

```
src/                         ← MOTOR DE DOMÍNIO (puro, sem importar configs/)
├── paths.py                     caminhos canônicos do projeto
├── specs.py                     contratos de entrada (Specs) + validação fail-fast
├── ambiente.py                  fábricas de Environment (ERA5 Reanalysis/Ensemble)
├── modelo.py                    resolver() → FogueteResolvido (modo="calculado")
├── modelos.py                   build_motor() e build_rocket(modo="calculado"|"medido")
├── inspecao.py                  relatórios formatados de motor, estrutura, segurança e voo
├── smoke.py                     executor da suíte automatizada de testes (pytest)
└── calculos/
    ├── motorlib_wrapper.py      adaptador OpenMotor (.ric → props + extração + solver)
    ├── motorlib_variacoes.py    overrides dot-path/wildcard em memória sobre props
    ├── motor.py                 derivar_motor(MotorSpec) → MotorDerivado (+ FS)
    ├── seguranca.py             fs_carcaca, check_p0, check_kn, check_mass_flux
    ├── componentes.py           TuboSpec / MassaPontualSpec → ComponenteDerivado
    ├── aletas.py                AletaSpec → AletaDerivada
    ├── aletas_rasaero.py        AletaSpec (SI) → AletaRASAero (polegadas)
    └── coifa.py                 CoifaSpec → CoifaDerivada

configs/                     ← DADOS PUROS E INSTÂNCIAS (zero I/O no import)
├── __init__.py                  fachada pública (reexporta Specs + HEFESTO)
├── material.py                  densidades e σ_lim
├── limites.py                   LIMITES_IREC (LimitesSeguranca)
└── foguetes/hefesto/            instância concreta do foguete Hefesto
    ├── __init__.py              HEFESTO (FogueteSpec completa)
    ├── corpo.py                 COMPONENTES (modo="calculado")
    ├── coifa.py                 COIFA_IREC (modo="calculado")
    ├── aletas.py                ALETA_IREC, ALETAS_TRAPEZIO_EQUIV
    ├── geometria.py             GEOMETRIA_MEDIDA_HEFESTO (modo="medido"), RAIL_BUTTONS
    ├── recuperacao.py           REEFED, UNREEFED
    ├── motor.py                 MOTOR_IREC (MotorSpec declarativa)
    ├── motor_variacoes.py       PARAMS_LIVRES, criar_variacao(), VARIACOES
    ├── voo.py                   IREC, IREC_E, IREC_ENSEMBLE_E
    └── estocastico.py           incertezas *_E para Monte Carlo

centralControle/             ← PAINEL OPERACIONAL (CLI)
├── rodar.py                     CLI unificada: sim | motor | estrutura | fs | dump | varrer | smoke
├── inspecionar.py               CLI de inspeção por seção
├── README.md                    manual operacional rápido
└── checklists.md                checklists de projeto e submissão

tests/                       ← SUÍTE AUTOMATIZADA (pytest)
├── test_specs_contratos.py      validação fail-fast e regra arquitetural (src ↛ configs)
├── test_calculos_estrutura.py   componentes, coifa, aletas, segurança e inércia
├── test_motor_e_variacoes.py    balística .ric/.eng e sincronização de overrides
└── test_integracao_voo.py       build_rocket (calculado vs medido) e voo RocketPy
```

## Como rodar

### Pela CLI (`centralControle/rodar.py`)

```bash
python centralControle/rodar.py smoke                  # roda todos os testes (pytest)
python centralControle/rodar.py fs                     # diagnósticos de segurança do motor
python centralControle/rodar.py motor                  # relatório completo do motor
python centralControle/rodar.py estrutura              # estrutura (compara calculado vs medido)
python centralControle/rodar.py dump                   # imprime toda a configuração
python centralControle/rodar.py sim                    # simulação determinística (modo calculado)
python centralControle/rodar.py sim --modo medido      # simulação determinística (modo medido)
python centralControle/rodar.py sim --motor throat_largo
python centralControle/rodar.py varrer                 # varredura empuxo × arrasto
python centralControle/rodar.py varrer-motor -p nozzle.throat=0.032:0.036:0.002
python centralControle/rodar.py analisar-motor
```

### Na IDE (`debug.py` ou `scripts/simDeterministica.py`)

Abra `debug.py` ou `scripts/simDeterministica.py`, ajuste as constantes no topo (`MODO_FOGUETE = "calculado" | "medido"`, `MOTOR`, etc.) e execute. Presets de variação de motor também podem ser acionados diretamente via CLI (`--motor throat_largo`).
