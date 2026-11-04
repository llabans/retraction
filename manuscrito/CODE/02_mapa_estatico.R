# Figura 3: mapa estático de ensayos retractados por país de realización (base 6).
# Usa el paquete maps (datos incluidos, sin descargas). Escribe FIGURES/static_retractions_world_map.png.
library(tidyverse)
library(haven)
library(here)
library(maps)
library(ggrepel)

data <- read_dta(here("DATA", "Base retraccion 6.dta"))

# nombres de país en la base -> nombres de la base de mapas `world`
pais_map <- c(
  "Alemania" = "Germany", "Australia" = "Australia", "Brasil" = "Brazil", "China" = "China",
  "Corea del Sur" = "South Korea", "EEUU" = "USA", "Egipto" = "Egypt", "España" = "Spain",
  "India" = "India", "Iran" = "Iran", "Italia" = "Italy", "Japon" = "Japan", "Kuwait" = "Kuwait",
  "México" = "Mexico", "Paises bajos" = "Netherlands", "Polonia" = "Poland", "Portugal" = "Portugal",
  "Reino Unido" = "UK", "República Democrática del Congo" = "Democratic Republic of the Congo",
  "Rusia" = "Russia", "Saudi Arabia" = "Saudi Arabia", "Taiwan" = "Taiwan", "Túnez" = "Tunisia"
)
counts <- data %>%
  mutate(region = unname(pais_map[str_squish(pais_eca)])) %>%
  filter(!is.na(region)) %>%
  count(region, name = "n")
sin_mapa <- setdiff(unique(str_squish(data$pais_eca)), c(names(pais_map), "Multinacional", "No esta explicito"))
if (length(sin_mapa) > 0) stop("Países sin correspondencia en el mapa: ", paste(sin_mapa, collapse = ", "))

world <- map_data("world") %>% filter(region != "Antarctica")
iso3 <- maps::iso3166 %>% distinct(mapname, a3) %>%
  mutate(region = str_remove(mapname, ":.*")) %>% distinct(region, .keep_all = TRUE)
labels <- world %>%
  group_by(region, group) %>% mutate(n_pts = n()) %>% ungroup() %>%
  group_by(region) %>% filter(n_pts == max(n_pts)) %>%           # parte principal del país
  summarise(long = mean(range(long)), lat = mean(range(lat)), .groups = "drop") %>%
  inner_join(counts, by = "region") %>%
  left_join(iso3 %>% select(region, a3), by = "region") %>%
  mutate(label = paste0(coalesce(a3, region), " (", n, ")"))

p <- ggplot() +
  geom_map(data = world, map = world, aes(map_id = region), fill = "grey92", colour = "grey60", linewidth = 0.1) +
  geom_map(data = counts, map = world, aes(map_id = region, fill = n), colour = "grey30", linewidth = 0.1) +
  expand_limits(x = world$long, y = world$lat) +
  scale_fill_viridis_c(name = "Retracted\ntrials", option = "plasma", direction = -1, begin = 0.1, end = 0.9,
                       breaks = scales::breaks_pretty(5)) +
  geom_text_repel(data = labels, aes(long, lat, label = label), size = 2.6, seed = 1234,
                  box.padding = 0.3, min.segment.length = 0, max.overlaps = Inf) +
  coord_quickmap(ylim = c(-56, 84)) +
  theme_void(base_size = 11) +
  theme(legend.position = c(0.08, 0.3), plot.background = element_rect(fill = "white", colour = NA))

ggsave(here("FIGURES", "static_retractions_world_map.png"), p, width = 10, height = 5.2, dpi = 300)
message("Mapa: ", sum(counts$n), " ensayos en ", nrow(counts), " países; sin país mapeable: ", nrow(data) - sum(counts$n))
