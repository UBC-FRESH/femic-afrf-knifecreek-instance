Data Publication Boundary
=========================

This is a public model instance. The boundary follows the same principle as the
sibling Gavin Lake instance: publish the open model and evidence, keep private
financial and personal material out.

Published surfaces
------------------

- documentation, ADRs, planning notes, and runbooks;
- the instance configuration and toolchain pin;
- reviewed data-acquisition manifests and checksums;
- reviewed stem-list manifests, with their synthetic or measured status;
- FVS-BC keyword sets, run manifests, and derived state-transition tables;
- the ws4 dataset inputs and evidence; and
- scenario definitions and results that have been reviewed for release.

Excluded surfaces
-----------------

- raw cost, revenue, contractor-rate, and cash-flow workbooks;
- private financial overlays;
- credentials, tokens, and private keys;
- machine-specific home directories and user profile paths;
- raw field data that AFRF has not cleared for publication; and
- third-party documents that cannot be redistributed.

Data sensitivity
----------------

Knife Creek source data may include culturally sensitive locations, rare
species, or commercial information. A layer is not public because it is
technically readable. Record the permission for each source before publishing
it.

If a source cannot be published, publish:

- the schema;
- the checksum of the private source;
- the transformation;
- the derived public summary; and
- a contact path for access.

That is enough to reproduce the model logic without republishing the source.

Audit
-----

Run the workflow validator before each push:

.. code-block:: bash

   python scripts/check_workflow.py

It rejects control characters, personal paths, and secret-shaped strings in
tracked text files.
