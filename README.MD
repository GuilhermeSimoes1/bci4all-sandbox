# BCI4ALL – Dataset P300 (Oddball visual, Unicorn BCI Core-8)

Autor: Guilherme | Data: 2026-10-20

## Conteúdo
| Ficheiro | Descrição |
|---|---|
| `session_p300_raw_<canal>.csv` | EEG contínuo **em bruto** (sem filtros) + canal de marcadores |
| `session_p300_epochs_Pz.npz` | Épocas já processadas do canal Pz  |
| `session_p300_epochs_PO7.npz` | Épocas já processadas do canal PO7 |
| `p300_Pz_stability.png` | Média ± 1σ (Target vs Non-Target) |
| `p300_Pz_sigma_over_time.png` | σ(t) Target vs Non-Target |
| `07_psychopy_single_stimulus.py` | Estimulação (PsychoPy, marcadores LSL no flip/V-Sync) |
| `05_p300_epoch_averaging.py` | Aquisição gpype, gravação, épocas e plots |
| `plot_utils.py` | Funções dos gráficos |

## Paradigma
- Oddball visual com 2 caixas: **A (esquerda) = Target**, B (direita) = Non-Target
- P(Target) = 0.20 | Flash = 125 ms | ISI = 800 ms | 150 ensaios por sessão
- Tarefa: fixar a caixa A e contar mentalmente os flashes de A
- Marcadores: `1` = Target, `2` = Non-Target, enviados via LSL no flip do ecrã

## Formato do CSV (bruto)
- **Frequência de amostragem:** 250 Hz (intervalo temporal fixo de 4.0 ms / 0.004 s).
- **Estrutura (10 colunas):**
  - Coluna 0 (`Time`): Tempo decorrido em segundos.
  - Colunas 1 a 8 (`Fz, C3, Cz, C4, Pz, PO7, POz, PO8`): Potencial em bruto (µV), sem filtros aplicados. 
  - Coluna 9 (`Ch09`): Canal de eventos discretos (`0` = repouso/sem flash, `1` = flash Alvo/Target, `2` = flash Não-Alvo/Non-Target).

## Formato do .npz (épocas já processadas/filtradas)
```python
d = np.load("session_p300_epochs_Pz.npz")
d["target_epochs"]     # (N_target, 225)  -> 225 amostras = [-100, 800] ms
d["nontarget_epochs"]  # (N_nontarget, 225)
d["time_axis"]         # ms
d["fs"], d["channel"]
