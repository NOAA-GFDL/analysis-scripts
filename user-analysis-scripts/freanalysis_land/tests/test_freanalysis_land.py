from freanalysis_land.land import LandAnalysisScript


def test_land_analysis_script():
    land = LandAnalysisScript()
    land.run_analysis("/work/a2p/lm4p2sc_GSWP3_hist_irr_catalog.json", ".")


if __name__ == "__main__":
    test_land_analysis_script()
