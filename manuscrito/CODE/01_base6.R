# Base 6: base 5 con las decisiones de elegibilidad y correcciones aprobadas por los autores el 2026-11-04
# (P-79, P-80, P-31). No modifica la base 5. Escribe:
#   DATA/Base retraccion 6.dta          base de análisis
#   TABLES/registro_base6.csv           cada exclusión, fila nueva y corrección, con su motivo
#
# Las decisiones registro por registro (ids, PMID, títulos) están en DATA/decisiones_base6.R, que NO se publica.
# Ese archivo define:
#   exclusiones      tribble(id, motivo)            artículos excluidos tras verificar el texto completo
#   correcciones     tribble(id, variable, valor_nuevo)   errores de transcripción
#   fila_nueva       list(id_origen, id, año_publicacion, titulo, autores, revisor, valor_despues, motivo)
#                    artículo retractado por la misma nota que otro registro y que faltaba en la base
#   no_aleatorizados vector de ids de ensayos no aleatorizados (análisis de sensibilidad solo ECA)
library(tidyverse)
library(haven)
library(here)

base5 <- read_dta(here("DATA", "Base retraccion 5 (cuartiles revisados).dta")) %>%
  mutate(id = round(id, 1))

source(here("DATA", "decisiones_base6.R"), encoding = "UTF-8")

# 1. Exclusiones
exclusiones <- exclusiones %>%
  mutate(grupo = case_when(str_starts(motivo, "Not a clinical trial") ~ "not_trial",
                           str_starts(motivo, "Secondary") ~ "secondary",
                           TRUE ~ "replacement"))

# 2. Correcciones de transcripción
base6 <- base5 %>% filter(!id %in% exclusiones$id)
antes <- base6
for (i in seq_len(nrow(correcciones))) {
  r <- correcciones[i, ]
  if (r$variable == "año_publicacion") {
    base6$año_publicacion[base6$id == r$id] <- as.numeric(r$valor_nuevo)
  } else {
    base6[[r$variable]][base6$id == r$id] <- r$valor_nuevo
  }
}
base6 <- base6 %>% mutate(tiempo_retracion = año_retraccion - año_publicacion)

# 3. Fila nueva: copia el registro de la misma nota y cambia los campos del artículo
nueva <- base6 %>% filter(id == fila_nueva$id_origen) %>%
  mutate(id = fila_nueva$id, año_publicacion = fila_nueva$año_publicacion,
         tiempo_retracion = año_retraccion - fila_nueva$año_publicacion,
         titulo = fila_nueva$titulo, autores = fila_nueva$autores, revisor = fila_nueva$revisor)
base6 <- bind_rows(base6, nueva) %>% arrange(id)

# 4. Diseño, para el análisis de sensibilidad solo con ECA
base6 <- base6 %>% mutate(ensayo_aleatorizado = as.numeric(!id %in% no_aleatorizados))
attr(base6$ensayo_aleatorizado, "label") <- "1 = randomised controlled trial; 0 = non-randomised or single-arm trial"

stopifnot(nrow(base6) == nrow(base5) - nrow(exclusiones) + 1, !any(duplicated(base6$id)))
write_dta(base6, here("DATA", "Base retraccion 6.dta"))

valor_antes <- function(id, v) as.character(antes[[v]][antes$id == id])
registro <- bind_rows(
  exclusiones %>% transmute(id, cambio = "excluido", variable = "", valor_antes = "", valor_despues = "", motivo, grupo),
  correcciones %>% rowwise() %>%
    transmute(id, cambio = "corregido", variable, valor_antes = valor_antes(id, variable), valor_despues = valor_nuevo,
              motivo = "Transcription error checked against PubMed (P-80)", grupo = "") %>% ungroup(),
  tibble(id = fila_nueva$id, cambio = "agregado", variable = "", valor_antes = "", valor_despues = fila_nueva$valor_despues,
         motivo = fila_nueva$motivo, grupo = ""),
  tibble(id = no_aleatorizados, cambio = "marcado", variable = "ensayo_aleatorizado", valor_antes = "", valor_despues = "0",
         motivo = "Non-randomised trial: kept (WHO/ICMJE definition); excluded in RCT-only sensitivity analysis", grupo = "")
)
write_csv(registro, here("TABLES", "registro_base6.csv"))
message("Base 6: ", nrow(base6), " ensayos; ", sum(base6$ensayo_aleatorizado), " ECA")
