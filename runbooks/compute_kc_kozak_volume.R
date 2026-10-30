#!/usr/bin/env Rscript
# Compute Kozak (2004) taper / merchantable volumes for KC tree records.
# Input CSV columns: row_id, species, dbh_cm, height_m
# Output CSV columns: row_id, merch_ht, stump_vol, top_vol, break_vol,
#                     merch_vol, wsv_vol

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) {
  stop("usage: compute_kc_kozak_volume.R input.csv output.csv")
}
input <- args[1]
output <- args[2]

source("Kozak_Parameters.R")
source("Diameter_Inside_Bark.R")
source("ProjectHeight.R")
source("LocateMerchHeight.R")
source("LogVolume.R")
source("Compute_Statistics.R")

trees <- read.csv(input, stringsAsFactors = FALSE)
trees$species <- toupper(trimws(trees$species))
# Map KC species to the 16 Kozak species groups.
map <- c(
  "FD" = "F", "FDI" = "F", "FDC" = "F",
  "PL" = "PL", "PLI" = "PL",
  "SE" = "S", "SX" = "S", "SW" = "S",
  "EP" = "E",
  "AT" = "AT",
  "OH" = "H", "H" = "H"
)
trees$sp0 <- unname(map[trees$species])
trees$sp0[is.na(trees$sp0)] <- "H"
trees$bgc.zone <- "IDF"
trees$height_m[!is.finite(trees$height_m) | trees$height_m <= 0] <-
  1.3 + 0.5 * trees$dbh_cm[!is.finite(trees$height_m) | trees$height_m <= 0]

volumes <- Compute.Statistics(
  trees$sp0,
  trees$bgc.zone,
  trees$dbh_cm,
  trees$height_m,
  d.at.brk = NA,
  proj.ht = NA,
  max.ht = 66,
  vers = 94,
  stump.ht = 0.3,
  merch.d = 10
)
result <- cbind(
  data.frame(row_id = trees$row_id),
  volumes
)
write.csv(result, output, row.names = FALSE)
