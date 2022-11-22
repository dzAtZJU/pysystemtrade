library(Quandl)
library(wavelets)
library(quantmod)

dji = getSymbols("^DJI", from = "2000-01-01", to = "2015-12-31")

dji = subset(dji, Date>="1961-05-17" & Date<"1962-11-02")
dji=dji[order(nrow(dji):1),]
dji = as.ts(dji$Value)
model = dwt(dji, filter="haar", n.levels=5)
plot(model)
imodel = idwt(model, fast=TRUE)

mmodal = modwt(dji, filter="la8", n.levels=5)
plot.modwt(mmodal)
