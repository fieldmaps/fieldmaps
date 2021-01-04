import React from 'react';

export default () => (
  <>
    <h1 className="has-text-centered">Boundary Methodology</h1>
    <p>
      For those looking to replicate or create workflows of their own, the
      following serves as a high-level overview of the steps carried out during
      spatial data processing to create the digital boundary file that can be
      clipped to any admin 0 layer. Source code used to perform transformations
      are available on{' '}
      <a href="https://github.com/fieldmaps/global-admin">GitHub</a>. The
      primary tools used in this pipeline include QGIS (through JSON batch
      files), GDAL (command line), and Pandas (table transformations).
    </p>
    <p className="has-text-centered">
      <img src="/img/tza-1.png" alt="Input boundaries 1" />
    </p>
    <p>
      Fig 1. The data processing pipeline takes the most detailed admin level
      available as the input.
    </p>
    <p className="has-text-centered">
      <img src="/img/tza-2.png" alt="Input boundaries 2" />
    </p>
    <p>
      Fig 2. From this input, the boundaries between admin regions are extended
      outwards using voronoi polygons.
    </p>
    <p className="has-text-centered">
      <img src="/img/tza-3.png" alt="Input boundaries 3" />
    </p>
    <p>
      Fig 3. The original input is dissolved with the resulting voronoi polygons
      to create a borderless digital boundary file.
    </p>
    <p className="has-text-centered">
      <img src="/img/tza-4.png" alt="Input boundaries 4" />
    </p>
    <p>Fig 4. This new layer can be clipped with any other admin 0 layer.</p>
    <h1 className="has-text-centered">Detailed Steps</h1>
    <ol>
      <li>
        Extract the edges of the boundary file as a line, while retaining
        information about which part of the line corresponds to which admin
        area. From this input, we want to extend these edges outwards in an
        intelligent way that will fill in space far beyond the original
        boundaries.
        <ol>
          <li>
            Start with the most detailed admin level available from the original
            source, with all attributes stripped except for codes used for
            joining.
          </li>
          <li>Dissolve to a single admin 0 polygon.</li>
          <li>
            Convert both the most detailed admin level and the dissolved admin 0
            layer from polygons to lines.
          </li>
          <li>
            Intersect line layers together, retaining information about which
            line segment originated from which detailed admin level.
          </li>
        </ol>
      </li>
      <li>
        Extract points along the lines to be used in generating voronoi
        polygons. Due to how voronoi polygons are generated, input points cannot
        be overlapping, so the ends of lines need to be trimmed an extremely
        small amount to allow a gap in between them. For this project, very
        small is defined as 0.000001 degrees (approx. 10cm)
        <ol>
          <li>
            Apply a very small buffer to each line segment without dissolving
            results.
          </li>
          <li>Convert the buffers into lines.</li>
          <li>
            Intersect the buffer lines with the line segments used at the
            beginning of this part. Use a line intersection tool to create
            points where these two layers meet. This will result in points
            located a very small distance from the ends of each line.
          </li>
          <li>
            Using these points placed almost at the end of every line segment,
            generate a buffer of 0.000002 degrees. This is to ensure that points
            next to each other will have their buffers fully overlapping.
            Dissolve results.
          </li>
          <li>
            With these small buffers covering the ends of every line segment,
            use the difference tool to very slightly trim each line segment, so
            their ends no longer touch.
          </li>
        </ol>
      </li>
      <li>
        In addition to creating points where boundaries meet along the edge,
        more points are required to generate a proper voronoi. Since voronoi
        complexity increases exponentially, adding points every few meters along
        a boundary would take days or weeks to process, especially for those
        with details coastlines (Chile, Indonesia, Philippines, etc). A better
        alternative is to use vertices only, although here line centroids are
        used instead, since using vertices sometimes introduce errors in the
        generated results.
        <ol>
          <li>
            The input line segments were exploded so that every strait part
            along them became its own feature.
          </li>
          <li>
            Points are generated by taking the centre of each exploded line
            part.
          </li>
          <li>
            Points generated in step 2.3 are combined with the steps above to
            create a single layer.
          </li>
        </ol>
      </li>
      <li>
        From these points spaced along the line, voronoi polygons intelligently
        extend outwards and allocate available space associated with the
        attributes of the edge point closest to it.
        <ol>
          <li>
            Generate voronoi polygons from the input points, filling an area
            double the size of the original bounding box of the input.
          </li>
          <li>Dissolve polygons that originate from the same admin polygon.</li>
          <li>
            Merge this dissolved layer with the original admin layer through a
            union.
          </li>
          <li>
            In the attribute table, in places where the original admin and the
            voronoi polygons intersect, ignore the voronoi attributes and use
            only the original. In places where there is only voronoi polygons,
            use those values. Merge polygons together that share the same
            attribute values.
          </li>
          <li>
            Apply topology cleaning to ensure the integrity of the final result.
          </li>
          <li>Create higher admin levels by dissolving based on attributes.</li>
          <li>Clip all layers to desired global admin 0 layer.</li>
        </ol>
      </li>
    </ol>
  </>
);