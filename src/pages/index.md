---
layout: ../layouts/Layout.astro
title: Home | Fieldmaps.io
active: ""
---

# Humanitarian Reference Maps

Fieldmaps is an initiative designed to address the needs of humanitarian field workers operating
in environments where data quality is variable, connectivity is sporadic, or where the context
changes frequently. It looks to consolidate work that has already been done within the
humanitarian community into living products designed for daily use. Beyond creating tools for
end-users, a primary focus is promoting inter-agency data sharing.

## Data

[![dataset coverage](/img/coverage.png)](/data)

The first part of this project is to create a living database that reflects the best available
reference data from multiple sources into a common format that is easy to use. The approach
taken here is to start with a baseline, typically OpenStreetMap, adding national sources that
have been reviewed by a UN agency, NGO, or other humanitarian actor.

To begin, work has been done cleaning up administrative boundaries to create a global
edge-matched layer to be used as a foundation for additional layers on top. This database starts
with countries which have undergone validation by UN OCHA for use as a common operational
dataset (COD). These datasets have been reviewed for quality and consistency at the national
level, so they are well aligned to fit into a global model with minimal transformations. For
countries not covered, geoBoundaries is used as a gap-filler until more authoritative sources
are available.

## Maps

[![atlas map](/img/atlas-ssd.png)](/maps)

The second part of this project strives to make dense and technical data accessible to the
widest possible audience. This comes from lessons learned in South Sudan and other countries in
the region, where extremely low bandwidth and a lack of geospatial expertise made it difficult
to put highly detailed databases into common use. A recurring problem was sharing datasets
containing 10,000+ populated places among field teams, each trying to communicate back complex
patterns of displacement between specific locations, often sharing similar colloquial names.
