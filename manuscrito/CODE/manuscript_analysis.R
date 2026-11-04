# Código de análisis del manuscrito "Retraction notes in clinical trials"
#
# Este script contiene SOLO los bloques de código R de manuscrito/CODE/manuscript.qmd, en el mismo orden.
# El texto del manuscrito y las cifras en línea (`r ...`) no se publican aquí. El .qmd completo y los datos
# quedan fuera del repositorio (ver README.md, sección "Datos").
#
# Entrada esperada (no incluida): manuscrito/DATA/Base retraccion 6.dta (la genera CODE/01_base6.R)
#                   y manuscrito/TABLES/registro_base6.csv (también de 01_base6.R)
# Salidas: tablas y figuras en manuscrito/TABLES/ y manuscrito/FIGURES/ (ignoradas por git)
# Ejecutar desde el proyecto manuscrito/retraction.Rproj (las rutas usan here::here()).
# Paquetes: ver manuscrito/CODE/paquetes_R.txt


## ---- setup ----  (opciones: setup, include=FALSE)
library(tidyverse)
library(haven)
library(labelled)
library(here)
library(officer)
library(flextable)
library(glue)
library(ggrepel)
library(knitr)

data <- read_dta(here("DATA", "Base retraccion 6.dta")) %>%
  mutate(across(where(is.labelled), as_factor)) %>%
  mutate(
    cuartil = paste0("Q", quartila_retrac),
    año_publicacion = as.numeric(as.character(año_publicacion)),
    año_retraccion = as.numeric(as.character(año_retraccion)),
    tiempo_hasta_retraccion = año_retraccion - año_publicacion
  ) %>%
  mutate(across(c(continente_ensayo, continente_1er_autor),
                ~ fct_recode(.x, Europe = "Europa", Multinational = "Multinacional", `Not explicit` = "No explicito")))

# Objects used in the abstract and in the results text.
# Percentages of reasons use the number of included trials as denominator.
n_total <- nrow(data)
# percentages are rounded half up (R's default rounds 56.25 down to 56.2)
r1 <- function(v) round(v + 1e-9, 1)
pct <- function(x, d = n_total) sprintf("%.1f", r1(100 * x / d))
n_si <- function(v) sum(v == "si", na.rm = TRUE)

period_labels <- c("2003-2007", "2008-2012", "2013-2017", "2018-2023")
n_period <- as.vector(table(cut(data$año_retraccion, c(2002, 2007, 2012, 2017, 2023), labels = period_labels)))
n_q <- as.vector(table(factor(data$cuartil, levels = paste0("Q", 1:4))))
n_early <- sum(data$año_retraccion <= 2012)
q1_early <- sum(data$año_retraccion <= 2012 & data$cuartil == "Q1")
q1_recent <- sum(data$año_retraccion >= 2018 & data$cuartil == "Q1")
q2_recent <- sum(data$año_retraccion >= 2018 & data$cuartil == "Q2")

t <- data$tiempo_hasta_retraccion
t_mean <- sprintf("%.1f", mean(t)); t_sd <- sprintf("%.1f", sd(t))
t_med <- sprintf("%.0f", median(t))
t_p25 <- sprintf("%.0f", quantile(t, 0.25)); t_p75 <- sprintf("%.0f", quantile(t, 0.75))
t_by_q <- function(q) sprintf("%.1f (SD %.1f)", mean(t[data$cuartil == q]), sd(t[data$cuartil == q]))

n_asia <- sum(data$continente_ensayo == "Asia")
n_africa <- sum(data$continente_ensayo == "Africa")
n_egypt <- sum(data$pais_eca == "Egipto")
asia_q1 <- sum(data$continente_ensayo == "Asia" & data$cuartil == "Q1")
africa_q2 <- sum(data$continente_ensayo == "Africa" & data$cuartil == "Q2")
n_asia_aut <- sum(data$continente_1er_autor == "Asia")
n_africa_aut <- sum(data$continente_1er_autor == "Africa")

n_fals <- n_si(data$falsificacion)
n_manip <- n_si(data$manipulacion); n_omis <- n_si(data$omision_info); n_unspec <- n_si(data$falsificacion_no_especif)
n_met <- n_si(data$errores_metodologicos_estadistic)
n_plag <- sum(data$plagio == "si" | data$autoplagio == "si" | data$plagio_a_otros == "si" | data$publi_duplicada == "si", na.rm = TRUE)
n_self <- n_si(data$autoplagio); n_other <- n_si(data$plagio_a_otros); n_dup <- n_si(data$publi_duplicada)
n_fab <- n_si(data$fabricacion)
main_reasons <- c("fabricacion", "falsificacion", "errores_metodologicos_estadistic", "plagio",
                  "salami", "errores_autoria", "revision_pares", "error_administ")
n_multi <- sum(rowSums(sapply(data[main_reasons], function(v) v == "si"), na.rm = TRUE) >= 2)

n_china <- sum(data$pais_eca == "China")
n_japan <- sum(data$pais_eca == "Japon")
n_fujii <- sum(str_detect(data$autores, "Fujii"), na.rm = TRUE)
n_sato <- sum(str_detect(data$autores, "^Sato Y"), na.rm = TRUE)
n_no_author <- sum(str_trim(data$autores) == "" | is.na(data$autores))
med_year_egypt <- median(data$año_retraccion[data$pais_eca == "Egipto"])
med_year_other <- median(data$año_retraccion[data$pais_eca != "Egipto"])
egypt_obgyn <- sum(data$pais_eca == "Egipto" &
                   str_detect(data$revista, regex("gyn|obstet|matern|pregnan|reprod|fertil|contracep", ignore_case = TRUE)))

n_year <- table(factor(data$año_retraccion, levels = 2003:2023))
max_before_2022 <- max(n_year[as.character(2003:2021)])
n_before18 <- sum(data$año_retraccion < 2018)
low_before18 <- sum(data$año_retraccion < 2018 & data$cuartil != "Q1")
low_recent <- sum(data$año_retraccion >= 2018 & data$cuartil != "Q1")

# Selection after full-text verification (TABLES/registro_base6.csv, written by CODE/01_base6.R)
registro <- read_csv(here("TABLES", "registro_base6.csv"), show_col_types = FALSE)
excl <- registro %>% filter(cambio == "excluido")
n_excl <- nrow(excl); n_excl_g <- function(g) sum(excl$grupo == g)
n_notices_assessed <- 119
n_articles_assessed <- n_total + n_excl
n_notices_incl <- n_notices_assessed - n_excl  # each excluded article had its own notice

# Sensitivity analysis restricted to randomised controlled trials
rct <- data$ensayo_aleatorizado == 1
n_rct <- sum(rct)
pct_rct <- function(x) sprintf("%.1f", r1(100 * sum(x & rct, na.rm = TRUE) / n_rct))
t_med_rct <- sprintf("%g", median(t[rct]))

# Time to retraction by reason, and trials by the two repeat authors (Fujii, Sato)
t_reason <- function(v) sprintf("%g years (IQR %g–%g)", median(t[v]),
                                round(quantile(t[v], 0.25), 1), round(quantile(t[v], 0.75), 1))
is_fab <- data$fabricacion == "si"
is_fals <- data$falsificacion == "si"
is_met <- data$errores_metodologicos_estadistic == "si"
is_plag <- coalesce(data$plagio == "si" | data$autoplagio == "si" | data$plagio_a_otros == "si" | data$publi_duplicada == "si", FALSE)
rep_auth <- coalesce(str_detect(data$autores, "Fujii") | str_detect(data$autores, "^Sato Y"), FALSE)
n_rep <- sum(rep_auth)
t_rep_med <- sprintf("%g", median(t[rep_auth]))
# journal names are spelled inconsistently in the dataset, so they are grouped ignoring case
j_key <- str_to_lower(str_squish(data$revista))
journals <- sort(table(j_key), decreasing = TRUE)
j_name <- function(k) { v <- unique(str_squish(data$revista)[j_key == k]); v[which.max(str_count(v, "[A-Z]"))] }
top_j <- sapply(names(journals)[1:2], j_name); top_n <- as.vector(journals)
n_fujii_cja <- sum(rep_auth & str_detect(data$revista, "Canadian Journal of Anesthesia"))

## ---- strobe_flowchart_LABEL ----  (opciones: strobe_flowchart_LABEL, echo=FALSE, message=FALSE, warning=FALSE)


library(DiagrammeR)
library(DiagrammeRsvg)
library(rsvg)

# Crea el flujo
graph <- grViz("
digraph strobe_flow {

  /*------  Global settings  ------*/
  graph   [rankdir = TB,
           nodesep = 0.5,
           ranksep = 0.8,
           bgcolor = white,
           fontname = 'Arial']

  node    [shape = box,
           style = 'rounded,filled',
           fontname = 'Arial',
           fontsize = 10,
           width = 4.0,
           height = 0.8,
           margin = 0.1]

  edge    [arrowhead = vee,
           penwidth = 1.5,
           color = '#333333']

  /*------  Node definitions  ------*/
  
  A [label = 'Records identified through\\nPubMed searching\\n(n = 76)',
     fillcolor = '#E3F2FD',
     color = '#1976D2']
     
  B [label = 'Records identified through\\nScopus searching\\n(n = 128)', 
     fillcolor = '#E3F2FD',
     color = '#1976D2']

  C [label = 'Records after duplicates removed\\n(n = 182)',
     fillcolor = '#E8F5E8',
     color = '#388E3C']

  D [label = 'Records screened\\n(n = 182)',
     fillcolor = '#E8F5E8',
     color = '#388E3C']

  E [label = 'Records excluded\\n(n = 63)\\n\\nAmendments/errata (n = 36)\\nNot clinical trials (n = 27)',
     fillcolor = '#FFEBEE',
     color = '#D32F2F',
     height = 1.2]

  F [label = 'Retraction notices assessed in full text\\n(n = 119; 121 retracted articles,\\ntwo notices retracted two articles each)',
     fillcolor = '#C8E6C9',
     color = '#2E7D32']

  X [label = 'Articles excluded after verification\\n(n = 9)\\n\\nNot a clinical trial in humans (n = 6)\\nSecondary publication without trial outcomes (n = 1)\\nRetraction and replacement (n = 2)',
     fillcolor = '#FFEBEE',
     color = '#D32F2F',
     height = 1.2]

  G [label = 'Retracted clinical trials included\\nin the analysis\\n(n = 112, from 110 notices)',
     fillcolor = '#A5D6A7',
     color = '#1B5E20']

  /*------  Hierarchical layout  ------*/
  {rank = same; A; B;}
  {rank = same; D; E;}
  {rank = same; F; X;}

  /*------  Connections  ------*/
  A -> C
  B -> C
  C -> D
  D -> F
  D -> E [constraint = false]
  F -> G
  F -> X [constraint = false]

  /*------  Duplicate removal indication  ------*/
  dup [label = 'Duplicates removed\\n(n = 22)',
       fillcolor = '#FFF3E0',
       color = '#F57C00',
       shape = oval,
       fontsize = 9,
       width = 2.5,
       height = 0.6]

  A -> dup [style = dotted, color = '#F57C00', constraint = false]
  B -> dup [style = dotted, color = '#F57C00', constraint = false]
  dup -> C [style = dotted, color = '#F57C00', constraint = false]
}
")

# Exporta a SVG y luego a PNG
flowchart_png <- here::here('FIGURES', 'strobe_flowchart.png')
export_svg(graph) |> charToRaw() |> rsvg_png(flowchart_png)

## ---- fig-strobe_flowchart ----
#| label: fig-strobe_flowchart
#| fig-cap: "Flow diagram of the selection of retraction notices (adapted from PRISMA 2020)"
#| fig-align: center
#| out-width: 100%

knitr::include_graphics(here::here('FIGURES', 'strobe_flowchart.png'))

## ---- create_summary_table ----  (opciones: create_summary_table)
## ---------------------------------------------------------------------
## TABLE: Retracted clinical trials (global and by quartile)
## ---------------------------------------------------------------------
# Cuartiles y totales (Q3 y Q4 agrupados: Q4 tiene n=1)
data_t1 <- data %>% mutate(cuartil = if_else(cuartil %in% c("Q3", "Q4"), "Q3–Q4", cuartil))
total_n <- nrow(data_t1)
quartile_labels <- c("Q1", "Q2", "Q3–Q4")
quartile_n <- sapply(quartile_labels, function(q) sum(data_t1$cuartil == q, na.rm = TRUE))
quartile_n_total <- sum(quartile_n)
quartile_headers <- sprintf("%s\nn=%d (%.1f%%)", quartile_labels, quartile_n, r1(100 * quartile_n / quartile_n_total))

# 1. Periodo de retracción (por año de retracción, no de publicación)
period_labels <- c("2003-2007", "2008-2012", "2013-2017", "2018-2023")
data_t1$periodo_retraccion <- cut(
  data_t1$año_retraccion,
  breaks = c(2003, 2007, 2012, 2017, 2023),
  right = TRUE,
  include.lowest = TRUE,
  labels = period_labels
)
period_tbl <- data_t1 %>%
  filter(!is.na(periodo_retraccion)) %>%
  count(periodo_retraccion, cuartil) %>%
  complete(periodo_retraccion, cuartil = quartile_labels, fill = list(n = 0)) %>%
  group_by(periodo_retraccion) %>%
  mutate(row_total = sum(n)) %>%
  ungroup() %>%
  filter(row_total > 0) %>%
  mutate(percent = ifelse(row_total > 0, r1(100 * n / row_total), 0)) %>%
  mutate(n_percent = sprintf("%d (%.1f)", n, percent)) %>%
  select(periodo_retraccion, cuartil, n_percent, row_total) %>%
  pivot_wider(names_from = cuartil, values_from = n_percent) %>%
  mutate(Global = sprintf("%d (%.1f)", row_total, r1(100 * row_total / total_n))) %>%
  select(periodo_retraccion, Global, all_of(quartile_labels)) %>%
  rename(Variable = periodo_retraccion)

# 2. Años hasta la retracción: mediana (RIC)
med_iqr <- function(x) sprintf("%g (%g–%g)", median(x), round(quantile(x, 0.25), 1), round(quantile(x, 0.75), 1))
years_by_q <- data_t1 %>%
  group_by(cuartil) %>%
  summarise(val = med_iqr(tiempo_hasta_retraccion), .groups = "drop") %>%
  pivot_wider(names_from = cuartil, values_from = val)
years_tbl <- bind_cols(tibble(Variable = "Years until retraction, median (IQR)*",
                              Global = med_iqr(data_t1$tiempo_hasta_retraccion)),
                       years_by_q[quartile_labels])

# 3. Continente del ensayo clínico (solo categorías presentes)
continents_ensayo <- levels(droplevels(data_t1$continente_ensayo))
data_t1$continente_ensayo <- factor(data_t1$continente_ensayo, levels = continents_ensayo)
cont_tbl <- data_t1 %>%
  filter(!is.na(continente_ensayo)) %>%
  count(continente_ensayo, cuartil) %>%
  complete(continente_ensayo, cuartil = quartile_labels, fill = list(n = 0)) %>%
  group_by(continente_ensayo) %>%
  mutate(row_total = sum(n)) %>%
  ungroup() %>%
  filter(row_total > 0) %>%
  mutate(percent = ifelse(row_total > 0, r1(100 * n / row_total), 0)) %>%
  mutate(n_percent = sprintf("%d (%.1f)", n, percent)) %>%
  select(continente_ensayo, cuartil, n_percent, row_total) %>%
  pivot_wider(names_from = cuartil, values_from = n_percent) %>%
  mutate(Global = sprintf("%d (%.1f)", row_total, r1(100 * row_total / total_n))) %>%
  select(continente_ensayo, Global, all_of(quartile_labels)) %>%
  rename(Variable = continente_ensayo)

# 4. Continente del país de filiación del primer autor (solo categorías presentes)
continents_autor <- levels(droplevels(data_t1$continente_1er_autor))
data_t1$continente_1er_autor <- factor(data_t1$continente_1er_autor, levels = continents_autor)
cont1_tbl <- data_t1 %>%
  filter(!is.na(continente_1er_autor)) %>%
  count(continente_1er_autor, cuartil) %>%
  complete(continente_1er_autor, cuartil = quartile_labels, fill = list(n = 0)) %>%
  group_by(continente_1er_autor) %>%
  mutate(row_total = sum(n)) %>%
  ungroup() %>%
  filter(row_total > 0) %>%
  mutate(percent = ifelse(row_total > 0, r1(100 * n / row_total), 0)) %>%
  mutate(n_percent = sprintf("%d (%.1f)", n, percent)) %>%
  select(continente_1er_autor, cuartil, n_percent, row_total) %>%
  pivot_wider(names_from = cuartil, values_from = n_percent) %>%
  mutate(Global = sprintf("%d (%.1f)", row_total, r1(100 * row_total / total_n))) %>%
  select(continente_1er_autor, Global, all_of(quartile_labels)) %>%
  rename(Variable = continente_1er_autor)

# 5. Razones de retracción (por fila)
det_reasons_vars <- c("fabricacion", "falsificacion", "manipulacion", "omision_info", "falsificacion_no_especif",
                  "errores_metodologicos_estadistic", "plagio", "autoplagio", "plagio_a_otros", "publi_duplicada",
                  "salami", "errores_autoria", "revision_pares", "error_administ")
det_reasons_labels <- c("Fabrication", "Falsification", "  Manipulation", "  Information omission", "  Unspecified falsification",
                    "Methodological and statistical problems", "Plagiarism", "  Self-plagiarism", "  Plagiarism of other authors", "  Duplicate publication",
                    "Salami publication", "Authorship problems", "Peer review errors", "Administrative errors")
reasons_tbl <- lapply(seq_along(det_reasons_vars), function(i) {
  var <- det_reasons_vars[i]
  label <- det_reasons_labels[i]
  temp <- data_t1 %>%
    mutate(present = !!as.name(var) == "si") %>%
    group_by(cuartil) %>%
    summarise(n = sum(present, na.rm = TRUE), .groups = "drop") %>%
    mutate(row_total = sum(n)) %>%
    ungroup() %>%
    filter(row_total > 0) %>%
    mutate(percent = ifelse(row_total > 0, r1(100 * n / row_total), 0)) %>%
    mutate(n_percent = sprintf("%d (%.1f)", n, percent)) %>%
    select(cuartil, n_percent, row_total) %>%
    pivot_wider(names_from = cuartil, values_from = n_percent) %>%
    mutate(Global = sprintf("%d (%.1f)", unique(row_total), r1(100 * unique(row_total) / total_n))) %>%
    mutate(Variable = label) %>%
    select(Variable, Global, all_of(quartile_labels))
  temp
}) %>% bind_rows()

# 6. Unir todas las tablas
table1 <- bind_rows(
  tibble(Variable = "Retraction notice publication period", Global = NA, Q1 = NA, Q2 = NA, `Q3–Q4` = NA),
  period_tbl,
  years_tbl,
  tibble(Variable = "Clinical trial continent", Global = NA, Q1 = NA, Q2 = NA, `Q3–Q4` = NA),
  cont_tbl,
  tibble(Variable = "First author's affiliation continent", Global = NA, Q1 = NA, Q2 = NA, `Q3–Q4` = NA),
  cont1_tbl,
  tibble(Variable = "Retraction reasons", Global = NA, Q1 = NA, Q2 = NA, `Q3–Q4` = NA),
  reasons_tbl
)

# 7. Flextable
ft1 <- flextable(table1) %>%
  set_header_labels(
    Variable = "Characteristics",
    Global = sprintf("Retracted clinical trials (n=%d)", total_n),
    Q1 = quartile_headers[1],
    Q2 = quartile_headers[2],
    `Q3–Q4` = quartile_headers[3]
  ) %>%
  theme_vanilla() %>%
  fontsize(size = 9) %>%
  width(j = 1, width = 3) %>%
  width(j = 2:5, width = 1.2) %>%
  align(align = "center", part = "header") %>%
  align(j = 2:5, align = "center", part = "body") %>%
  bold(part = "header") %>%
  bold(i = ~is.na(Global), part = "body") %>%
  italic(i = ~is.na(Global), part = "body") %>%
  add_footer_lines(paste0("Global column: n (% of all trials, n=", total_n, "). Quartile columns: n (row %). Q3 and Q4 are grouped because only ", sum(data$cuartil == "Q4"), " trial(s) were in a Q4 journal. *Time from publication to retraction in years. A trial could have more than one reason for retraction, so reasons do not add up to the total; subcategories (indented) are not mutually exclusive.")) %>%
  fontsize(size = 8, part = "footer") %>%
  italic(part = "footer")

# 8. Guardar tabla
save_as_docx(ft1, path = here::here('TABLES', 'Table_ensayos_retractados.docx'))
saveRDS(ft1, file = here::here('TABLES', 'Table_ensayos_retractados.rds'))

## ---- tbl-table1 ----
#| label: tbl-table1
#| tbl-cap: "Characteristics of retracted clinical trials by SCImago quartile of the journal at the time of retraction"

ft1 <- readRDS(here::here('TABLES', 'Table_ensayos_retractados.rds'))
ft1  # Si el objeto es flextable, esto lo mostrará correctamente en Quarto

## ---- plot_data_prep ----  (opciones: plot_data_prep)
# import  # Data
# Asegurar que año_retraccion sea numérico antes de cualquier operación
data <- data %>%
  mutate(
    año_retraccion = as.numeric(as.character(año_retraccion)),
    cuartil = as.factor(cuartil)
  )


plot_data <- data %>%
    group_by(año_retraccion, cuartil) %>%
    summarise(frecuencia = n(), .groups = "drop") %>%
    # Asegurar que año_retraccion siga siendo numérico después del group_by
    mutate(año_retraccion = as.numeric(año_retraccion))

años_nivel <- 2003:2023
cuartiles_nivel <- c("Q1", "Q2", "Q3", "Q4")



plot_data <- plot_data %>%
    complete(
        año_retraccion = años_nivel,
        cuartil = cuartiles_nivel,
        fill = list(frecuencia = 0)
    ) %>%
    # Mantener año_retraccion como numérico después de complete()
    mutate(año_retraccion = as.numeric(año_retraccion))


# table trends line  
totals <- plot_data %>%
    group_by(año_retraccion) %>%
    summarize(total_frecuencia = sum(frecuencia)) %>%
    ungroup() %>%
    # Asegurar que año_retraccion sea numérico en totals también
    mutate(año_retraccion = as.numeric(año_retraccion))

## ---- create_figure_retraction ----  (opciones: create_figure_retraction)

grafico <- ggplot(plot_data, aes(x = año_retraccion, y = frecuencia, fill = cuartil)) +
  geom_bar(stat = "identity", position = "stack", width = 0.8) +
   

  # Línea de tendencia basada en los totales
  geom_line(
    data = totals, 
    aes(x = año_retraccion, y = total_frecuencia), 
    color = "black",      # Color de la línea
    size = 1.2,           # Grosor de la línea
    group = 1,             # Agrupación para asegurar una línea continua
    inherit.aes = FALSE   
    ) +
  
  # Puntos en la línea de tendencia
  geom_point(
    data = totals, 
    aes(x = año_retraccion, y = total_frecuencia), 
    color = "black",      # Color de los puntos
    size = 3,              # Tamaño de los puntos
    inherit.aes = FALSE
    ) +
  
  # Etiquetas de los totales encima de cada barra
  geom_text(
    data = dplyr::filter(totals, total_frecuencia > 0), 
    aes(x = año_retraccion, y = total_frecuencia, label = total_frecuencia),
    vjust = -0.5,         # Posicionamiento vertical encima de la barra
    size = 3.5,           # Tamaño de la etiqueta
    color = "black",
    inherit.aes = FALSE
  ) +
  
  scale_fill_manual(
    values = c(
      "Q1" = "#0072B2",
      "Q2" = "#E69F00",
      "Q3" = "#009E73",
      "Q4" = "#CC79A7"
    ),
    name = "SCImago quartile"
  ) +
  scale_y_continuous(
    limits = c(0, 25), 
    expand = c(0, 0)   
  ) +
  labs(
    x = "Year of retraction",
    y = "Number of retracted trials"
    #caption = "Fuente: Elaboración propia"
  ) +
  theme_minimal(base_size = 14) +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold"),
    plot.subtitle = element_text(hjust = 0.5, face = "italic"),
    axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1),
    legend.position = "bottom"
  ) +  scale_x_continuous(
    breaks = seq(2003, 2023, by = 1)
  )
ggsave(
  filename = here::here('FIGURES', 'line_bar_stacked.png'),
  plot = last_plot(),
  width = 8, height = 5, dpi = 300
)

## ---- fig-retract_fig2 ----
#| label: fig-retract_fig2
#| fig-cap: !expr paste0("Retracted clinical trials by year of retraction and SCImago quartile of the journal, 2003–2023 (n=", n_total, "). 2023 includes retractions up to 7 August.")
#| fig-width: 12
#| fig-height: 8
#| fig-align: center
#| out-width: "100%"
#| fig-pos: "center"

# Apply knitr::include_graphics to show the image
knitr::include_graphics(here::here('FIGURES', 'line_bar_stacked.png'))

## ---- world_map_animation ----  (opciones: world_map_animation)
data <- read_dta(here("DATA", "Base retraccion 6.dta")) %>%
    mutate(across(where(is.labelled), as_factor)) %>%
    # Create quartile variable with appropriate labels
    mutate(cuartil = case_when(
        quartila_retrac == 1 ~ "Q1",
        quartila_retrac == 2 ~ "Q2",
        quartila_retrac == 3 ~ "Q3",
        quartila_retrac == 4 ~ "Q4",
        TRUE ~ as.character(quartila_retrac)
    )) %>% # Create time to retraction variable
    mutate(tiempo_hasta_retraccion = año_retraccion - año_publicacion)

# crear variable de periodo de publicación

# convertir año_publicacion a numérico
data <- data %>%
    mutate(año_publicacion = as.numeric(as.character(año_publicacion)))


data <- data %>%
    mutate(periodo_publicacion = case_when(
        año_publicacion >= 2003 & año_publicacion <= 2007 ~ "2003-2007",
        año_publicacion >= 2008 & año_publicacion <= 2012 ~ "2008-2012",
        año_publicacion >= 2013 & año_publicacion <= 2017 ~ "2013-2017",
        año_publicacion >= 2018 & año_publicacion <= 2023 ~ "2018-2023",
        TRUE ~ NA_character_
    ))

# Harmonize pais_eca for mapping and tables
# Exclude 'Multinacional' and 'No esta explicito' for mapping
data <- data %>%
    mutate(pais_eca_harmonized = recode(pais_eca,
        "Alemania" = "Germany",
        "Australia" = "Australia",
        "Brasil" = "Brazil",
        "China" = "China",
        "Corea del Sur" = "South Korea",
        "EEUU" = "United States of America",
        "Egipto" = "Egypt",
        "España" = "Spain",
        "India" = "India",
        "Iran" = "Iran",
        "Italia" = "Italy",
        "Japon" = "Japan",
        "Kuwait" = "Kuwait",
        "México" = "Mexico",
        "Paises bajos" = "Netherlands",
        "Polonia" = "Poland",
        "Portugal" = "Portugal",
        "Reino Unido" = "United Kingdom",
        "República Democrática del Congo" = "Democratic Republic of the Congo",
        "Rusia" = "Russia",
        "Saudi Arabia" = "Saudi Arabia",
        "Taiwan" = "Taiwan",
        "Túnez" = "Tunisia",
        "Multinacional" = NA_character_,
        "No esta explicito" = NA_character_
    ))

# ═══════════════  LIBRARIES  ═════════════════════════════════════════════
needed <- c(
    "tidyverse", "sf", "rnaturalearth", "countrycode",
    "gganimate", "gifski", "av"
) # av ≥ 0.10
to_install <- needed[!needed %in% installed.packages()[, "Package"]]
if (length(to_install) > 0) stop("Missing packages: ", paste(to_install, collapse = ", "))

library(tidyverse)
library(sf)
library(rnaturalearth)
library(countrycode)
library(gganimate)

# Crear shapefile mundial antes de cualquier uso
world <- ne_countries(scale = "medium", returnclass = "sf") %>%
  select(iso_a3, name_long, geometry)

# ═══════════════  1. RETRACTIONS BY COUNTRY & YEAR  ══════════════════════
ret_cty_year <- data %>%
    filter(!is.na(pais_eca_harmonized), !is.na(año_retraccion)) %>%
    mutate(iso3 = countrycode(pais_eca_harmonized, # convierte a ISO-3
        origin = "country.name",
        destination = "iso3c",
        custom_match = c("Europe" = NA)
    )) %>% # ej. si hubiera un agregado
    filter(!is.na(iso3)) %>% # descarta países no mapeables
    count(iso3, año_retraccion, name = "n_ret")

# Crear etiquetas solo para países con retractions totales > 0
labels_df <- world %>%
  left_join(
    ret_cty_year %>% group_by(iso3) %>% summarise(total_ret = sum(n_ret, na.rm = TRUE), .groups = "drop"),
    by = c("iso_a3" = "iso3")
  ) %>%
  filter(total_ret > 0, !is.na(total_ret)) %>%
  mutate(
    centro = st_point_on_surface(geometry),
    lon = st_coordinates(centro)[, 1],
    lat = st_coordinates(centro)[, 2],
    label_iso = as.character(iso_a3)
  ) %>%
  st_drop_geometry()

# ═══════════════  2. WORLD SHAPEFILE  ════════════════════════════════════
world <- ne_countries(scale = "medium", returnclass = "sf") %>%
    select(iso_a3, name_long, geometry)

# ═══════════════  3. JOIN + COMPLETE DATA FOR ALL YEARS  ═════════════════
# Create a complete grid of all countries and all years
all_years <- sort(unique(ret_cty_year$año_retraccion))
all_countries <- world$iso_a3

# Create complete combination and join
world_year <- world %>%
    crossing(año_retraccion = all_years) %>%  # All countries for all years
    left_join(ret_cty_year, by = c("iso_a3" = "iso3", "año_retraccion")) %>%
    mutate(n_ret = replace_na(n_ret, 0))

# Sólido para ‘limits’
max_ret <- max(world_year$n_ret, na.rm = TRUE)

# Filtrar solo filas con geometría válida para graficar
world_year_plot <- world_year %>% filter(!st_is_empty(geometry) & !is.na(geometry))

# ── 4. MAPA BASE ─────────────────────────────────────────────────────────
base_map <- ggplot(world_year_plot) +
    geom_sf(aes(fill = n_ret), colour = "grey30", size = 0.1) +
    scale_fill_viridis_c(
        name = "Retractions\nper Year",
        option = "viridis",      # Diferente del estático (plasma)
        direction = 1,           
        begin = 0.2,             # Más claro que el estático
        end = 0.95,              # Hasta colores más intensos
        limits = c(0, max_ret),
        breaks = c(0, 1, 2, 3, 4, 5, 6, 7, 8),  # Más escalas detalladas
        na.value = "grey90",     # Gris claro para países sin datos
        guide = guide_colorbar(
            title.position = "top",
            title.hjust = 0.5,
            barwidth = unit(1.2, "cm"),
            barheight = unit(8, "cm"),
            frame.colour = "black",
            ticks.colour = "black"
        )
    ) +
    coord_sf() +
    geom_text_repel(
        data = labels_df,
        aes(x = lon, y = lat, label = label_iso),
        size = 2.8,
        colour = "black",
        seed = 1234,
        box.padding = 0.25,
        max.overlaps = Inf,
        force = 0.5
    ) +
    labs(
        subtitle = "Annual retractions by country of trial conduct",
        caption = "Source: Own elaboration"
    ) +
    theme_void(base_size = 11) +
    theme(
        plot.title = element_text(face = "bold", hjust = 0.5, size = 15,
                                  color = "#2c3e50", margin = margin(b = 8)),
        plot.subtitle = element_text(face = "italic", hjust = 0.5, size = 11,
                                     color = "#34495e", margin = margin(b = 6)),
        plot.caption = element_text(hjust = 1, size = 8, color = "#7f8c8d"),
        legend.position = "right",
        legend.title = element_text(size = 9, face = "bold", color = "#2c3e50"),
        legend.text = element_text(size = 8, color = "#2c3e50"),
        panel.background = element_rect(fill = "white", color = NA),
        plot.background = element_rect(fill = "white", color = NA),
        plot.margin = margin(10, 10, 10, 10)
    )
# ...existing code...

## ---- fig-retract_world ----
#| label: fig-retract_world
#| fig-cap: "Retracted clinical trials by country of trial conduct, 2003–2023. Multinational trials and trials without an explicit country are not shown."
#| fig-width: 12
#| fig-height: 8
#| fig-align: center
#| out-width: "100%"
#| fig-pos: "center"

# Apply knitr::include_graphics to show the image
knitr::include_graphics(here::here('FIGURES', 'static_retractions_world_map.png'))

## ---- generate_s1_table_rds ----  (opciones: generate_s1_table_rds, include=FALSE)
library(dplyr)
library(tidyr)
library(flextable)
library(here)

# Definir periodos
period_labels <- c("2003-2007", "2008-2012", "2013-2017", "2018-2023")

# Variables y etiquetas
reasons_vars <- c(
  "fabricacion", "falsificacion", "manipulacion", "omision_info", "falsificacion_no_especif",
  "errores_metodologicos_estadistic", "plagio", "autoplagio", "plagio_a_otros", "publi_duplicada",
  "salami", "errores_autoria", "revision_pares", "error_administ"
)
reasons_labels <- c(
  "Fabrication", "Falsification", "Manipulation", "Information omission", "Unspecified falsification",
  "Methodological and statistical problems", "Plagiarism", "Self-plagiarism", "Plagiarism of other authors", "Duplicate publication",
  "Salami publication", "Authorship problems", "Peer review errors", "Administrative errors"
)

# Asignar periodo
data2 <- data %>%
  mutate(period = case_when(
    año_retraccion >= 2003 & año_retraccion <= 2007 ~ "2003-2007",
    año_retraccion >= 2008 & año_retraccion <= 2012 ~ "2008-2012",
    año_retraccion >= 2013 & año_retraccion <= 2017 ~ "2013-2017",
    año_retraccion >= 2018 & año_retraccion <= 2023 ~ "2018-2023",
    TRUE ~ NA_character_
  ))

# Datos largos
long <- data2 %>%
  select(period, all_of(reasons_vars)) %>%
  pivot_longer(cols = all_of(reasons_vars), names_to = "reason", values_to = "present") %>%
  filter(!is.na(period), present == "si") %>%
  mutate(reason = factor(reason, levels = reasons_vars, labels = reasons_labels))

# Conteo n por razón y periodo
table_s1 <- long %>%
  group_by(reason, period) %>%
  summarise(n = n(), .groups = "drop") %>%
  complete(reason = reasons_labels, period = period_labels, fill = list(n = 0))

# Calcular totales por razón (fila)
row_totals <- table_s1 %>%
  group_by(reason) %>%
  summarise(total = sum(n), .groups = "drop")

# Unir totales y calcular porcentaje por fila
table_s1 <- table_s1 %>%
  left_join(row_totals, by = "reason") %>%
  mutate(
    percent = ifelse(total > 0, r1(100 * n / total), 0),
    n_percent = sprintf("%d (%.1f)", n, percent)
  ) %>%
  select(reason, period, n_percent) %>%
  pivot_wider(names_from = period, values_from = n_percent) %>%
  arrange(factor(reason, levels = reasons_labels))

# Encabezados de periodo con n
period_n <- sapply(period_labels, function(p) sum(data2$period == p, na.rm = TRUE))
period_headers <- sprintf("%s\nn=%d (%.1f%%)", period_labels, period_n, r1(100 * period_n / sum(period_n)))

ft_s1 <- flextable(table_s1) %>%
  set_header_labels(
    reason = "Retraction Reason",
    `2003-2007` = period_headers[1],
    `2008-2012` = period_headers[2],
    `2013-2017` = period_headers[3],
    `2018-2023` = period_headers[4]
  ) %>%
  theme_vanilla() %>%
  fontsize(size = 9) %>%
  width(j = 1, width = 2.5) %>%
  width(j = 2:5, width = 1.2) %>%
  align(align = "center", part = "header") %>%
  align(j = 2:5, align = "center", part = "body") %>%
  bold(part = "header") %>%
  padding(i = ~ stringr::str_starts(reason, "  "), j = 1, padding.left = 20) %>%
  add_footer_lines("The sum of retraction reasons may not match the total n as some cases reported more than 1 retraction reason.") %>%
  fontsize(size = 8, part = "footer") %>%
  italic(part = "footer")

# Guardar tabla
saveRDS(ft_s1, file = here::here('TABLES', 'Table_S1_reasons_by_period.rds'))

## ---- tbl_s1_reasons_by_period ----  (opciones: tbl_s1_reasons_by_period)
#| label: tbl-s1
#| tbl-cap: !expr paste0("Table S1. Reasons for retraction of clinical trials by period of retraction (n=", n_total, "). A trial could have more than one reason.")

ft_s1 <- readRDS(here::here('TABLES', 'Table_S1_reasons_by_period.rds'))
ft_s1  # Solo mostrar si es flextable, no imprimir tibbles/data.frames
