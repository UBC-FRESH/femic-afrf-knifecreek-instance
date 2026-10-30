# Knife Creek ws4 recipe

`forestmodel.xml` is the KC ForestModelXML recipe. `fragments.csv` is the
matrix-builder fragment inventory.

The recipe is generated from the current KC H-matrix tables by
`runbooks/build_kc_forestmodel_xml.py`. It is compiled with the WS4 matrix
builder:

```bash
ws4 build --xml data/kc_ws4_recipe/forestmodel.xml \
  --fragments data/kc_ws4_recipe/fragments.csv \
  --out ws4/dataset_kc_v1
ws4 validate --dataset ws4/dataset_kc_v1
```

The six state fields are `GWM`, `BA`, `QMD`, `LT`, `RES` and `HMZ`. `AU` is a
constant compatibility field. `IFM`, `ORIGIN` and `RETENTION` are explicit
because the ForestModelXML contract keeps eligibility, provenance and retention
separate.

This is a structural recipe. It is not calibrated to Knife Creek, does not
contain a clearcut, and is not a legal-compliance model. `F_AGE` is VRI
projected age, not a measured stand age. The 100-year feature curves are
space-for-time curves; product yield remains point estimates.
