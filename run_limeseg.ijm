run("Show GUI"); // Initializes LimeSeg
idImage = getImageID();
run("Clear all");

// Set the cell_id variable to the desired value
cell_id = 1109311;

path = "C:/Users/shil5659/OneDrive - Nexus365/Documents/GitHub/cell_shape_toolkit/";

// This table contains nuclear positions, from another segmentation method
// eg. spot detection, or cellpose segmentation 
open(path + "output/cell_positions/" + cell_id + "_0.csv");
Table.rename(cell_id + "_0.csv", "Results");
z_scale = 1;
roiManager("reset");

// Define the batch size (100 cells per batch)
batchSize = 100;
nCells = nResults() - 1; // Adjust for 0-based index

//add cells to the ROI manager, to segment 
for (startCell = 1; startCell < nCells; startCell += batchSize) {
	
	run("Clear all");
	
	open(path + "output/cell_positions/" + cell_id + "_0.csv");
	Table.rename(cell_id + "_0.csv", "Results");
	
    // Clear the ROI manager for each batch
    roiManager("reset");

    for (i = startCell; i < Math.min(startCell + batchSize, nCells); i++) {
        xp = getResult("X", i);//for now in XYZ format 
        yp = getResult("Y", i);
        zp = getResult("Z", i)+1;
        radius = 10; // optimize this for your cell size! Larger is better, but it's important that none of your ROIs overlap with cell boundaries. 
		setSlice(zp); 
		makeOval(xp-radius,yp-radius,2*radius,2*radius);
        Roi.setPosition(1, zp, 1);
        roiManager("Add");
    }
    
    close("Results");
    
    

    // Prepare to work on the initial image
    selectImage(idImage);
// Actually run limeseg. Optimize parameters here. 
run("Sphere Seg", "d_0=2 f_pressure=0.01 " +
    "z_scale=1 range_in_d0_units=2 " +
    "samecell=false show3d=true " +
    "numberofintegrationstep=5000 " + 
    "color=(0,0,0) " + 
    "realxypixelsize=0.25");

    print("LimeSeg finished for batch " + (startCell / batchSize));
    
   fname = path + "output/limeseg_output/"+toString(cell_id)+"/" + toString(cell_id) + "_" + toString((startCell-1) / batchSize); 
   print(fname);
   File.makeDirectory(fname);
   
   

    // Save the LimeSeg output for this batch
    Ext.saveStateToXmlPly(fname);
    
    // save the Results window 
    selectWindow("Results");
    saveAs("results", fname + "/Results.csv");
}

print("Analysis and saving completed");
