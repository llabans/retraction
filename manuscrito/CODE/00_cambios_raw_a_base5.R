# Registro de cambios entre la base RAW y la base 5 (cuartiles revisados).
# Genera TABLES/cambios_raw_a_base5.csv con una fila por cambio (id, variable, valor antes y después).
# Las columnas `motivo` y `revisor` quedan vacías para que los autores las completen (P-47).
library(tidyverse)
library(haven)
library(here)

as_text <- function(d) d %>% mutate(id = round(as.numeric(id), 1),
                                    across(where(is.labelled), ~ as.character(as_factor(.x))),
                                    across(everything(), as.character))
raw <- read_dta(here("RAW", "data_rectraction.dta")) %>%
  rename(any_of(c(continente_ensayo = "continente_eca",
                  continente_1er_autor = "continente_primer_autor",
                  falsificacion_no_especif = "falsificacion_no_especifica"))) %>%
  as_text()
base5 <- read_dta(here("DATA", "Base retraccion 5 (cuartiles revisados).dta")) %>% as_text()

vars <- setdiff(intersect(names(raw), names(base5)), "id")
long <- function(d, nm) d %>% select(id, all_of(vars)) %>%
  pivot_longer(-id, names_to = "variable", values_to = nm)
cambios <- inner_join(long(raw, "valor_raw"), long(base5, "valor_base5"), by = c("id", "variable")) %>%
  filter(coalesce(str_squish(valor_raw), "<NA>") != coalesce(str_squish(valor_base5), "<NA>")) %>%
  mutate(motivo = "", revisor = "") %>%
  arrange(variable, as.numeric(id))

write_csv(cambios, here("TABLES", "cambios_raw_a_base5.csv"), na = "")
message(nrow(cambios), " cambios en ", n_distinct(cambios$variable), " variables; ",
        "ids solo en RAW: ", paste(setdiff(raw$id, base5$id), collapse = ", "),
        "; ids solo en base 5: ", paste(setdiff(base5$id, raw$id), collapse = ", "))
