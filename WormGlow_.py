from ij import *
from ij import IJ, ImagePlus, Macro
from ij.gui import Roi, PointRoi, GenericDialog, Overlay, HistogramWindow 
from ij.plugin import Duplicator, Straightener, Selection
from ij.plugin.frame import RoiManager
from ij.io import FileSaver
from ij.process import ImageStatistics
import csv

def masking_macro(image_plus, dialog_value):
    IJ.run("Enhance Contrast...", "saturated=0.3 normalize")
    IJ.run(image_plus, "Find Edges", "slice")
    IJ.run(image_plus, "Auto Threshold", "method=Minimum white")
    Macro.setOptions("BlackBackground")
    for i in range(0,dialog_value):
        IJ.run(image_plus, "Dilate", "slice")  
    IJ.run("Analyze Particles...", "size=5000-Infinity show=Masks add in_situ")
    IJ.run("Create Selection")

def run_script():

    imgplus = IJ.getImage()  # Gets entire ImageStack of loaded images, packaged in an ImagePlus object
    transform = imgplus.duplicate()
    print(type(imgplus))
    current = IJ.getProcessor()  # Gets current image shown in ACTIVE window (ImageProcessor)

    print(imgplus)  # Outputs image details to console
    
    orig_selection = imgplus.getOverlay()  # Object containing line selections
    transform.setOverlay(orig_selection)
    line_selection = transform.getOverlay().iterator()
    
    number_worms = 1  # Counter for number of worms selected

    working_img = current.duplicate()

    # Dialog box to select masking sensitivity (number of times to run DILATE)
    dialog = GenericDialog("Choose Masking Sensitivity")
    dialog.addSlider("Sensitivity", 1, 10, 3)
    dialog.hideCancelButton()
    dialog.showDialog()
    value = dialog.getSliders().get(0).getValue()  # Get dialog slider selection
    
    imp = ImagePlus("Masking Result", working_img)  # Creates an ImagePlus object for current image displayed in window 
    imp.show()
    
    roiman = RoiManager()  # Creates instance of RoiManager
 
    masking_macro(imp, value)  # Runs masking & dilate specified number of times

    transform.show()
    transform_stack = transform.getStack()
    num_slices = transform_stack.getSize()
    for slice in range(1, num_slices+1):
        current_processor = transform_stack.getProcessor(slice)
        current_processor.setColor(0)
        current_processor.fillOutside(roiman.getRoi(roiman.getCount() -1))

    roiman.reset()  # Clears ROI manager after background is removed
    
    roiman.setOverlay(transform.getOverlay())  # Sets worm selection as Overlay
    print(roiman.getCount())  # Prints number of worms selected for verification

    for line in line_selection:  # Iterates through worms selected (in order of selection)
        line_width = line.getStrokeWidth()  # Line width as selected in segmented line settings
        print(line)
        print("current roi " + transform.getOverlay().get(number_worms -1).toString())
        roiman.select(number_worms -1)
        print(transform.getTitle())
        command = "title=" + transform.getTitle() + " line=" + str(int(line_width)) + " process"
        IJ.run("Straighten...", command)  # Runs ImageJ built in "Straighten" tool on selection
        
        polygon = line.getPolygon()  # Prints coordinates of selected worms to console
        x_points = polygon.xpoints
        y_points = polygon.ypoints
        print("worm" + str(number_worms))
        for i in range(0, len(x_points)):
            print(x_points[i], y_points[i])  # Prints coordinates of each point on polyline
        number_worms += 1  # Increments worm number bc iterator can only be FIFO

    IJ.run("Surface Plot...", "polygon=100 shade draw_axis smooth stack")  # Runs "Surface Plot" with default options

if __name__ in ['__builtin__', '__main__']:
    run_script()
