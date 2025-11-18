Meshery is a tool that generates base course meshes from an SVG file and raw height map.

## Getting Started

1. Download and install the latest release for windows or mac from the releases page.

### Prepping your files

#### SVG File

SVG files are usually automatically during the [Course Terrain Tool](https://help.opengolfsim.com/tools/course-terrain-tool/) steps of the course building process. However, you can also create SVGs from scratch for test or fantasy courses.

- Your SVG file should contain a layer group with an `id` of `course`. All course elements like fairway, bunker, green shapes should be placed within that group. All other groups/layers in the SVG will be ignored. This is useful for stashing guide layers or satellite or hillside images.
- The vector shapes should be color coded to surfaces (fairway, bunker, etc.) using the official OGS color pallette.
- Shapes need to be fully closed paths (no lines or objects). Make sure you convert any lines to closed path shapes.
- Try and avoid sharp corners, or overlapping holes. 

#### Unity Raw Heightmap Export

- In the inspector, under your terrain's Settings tab, select **Export Raw**
  - Depth: **Bit 16**
  - Byte Order: **Windows**
  - Flip Vertically: **True**
- Click **Export**


### Generating Meshes

To generate your meshes:

1. Open **OGS Meshery**
2. Set the **SVG file** for your course
3. Set the **RAW terrain** file for your course
4. Set the **Output Folder** we should write the meshes to.
5. Set the terrain **height scale**. (Usually found in your terrain stats CSV file)
6. Click **Generate Meshes** to start the process.
7. Once completed the generated OBJ files should be found in the output folder you selected.

The OGS SDK for Unity contains an import tool for automating the process of importing these meshes and batch assigning their materials. Follow the Unity SDK guide for importing and customizing meshes.

> [!WARNING]
> Note: Fow now, after importing the obj files into Unity, you likely need to manually reposition the imported mesh to line up with the terrain. It should be some variation of the terrain width height set on the x,z values in unity (try positive negative or halving the width/height). We're still working on this bug.

---


### Development

If you want to checkout and run this repository on your local machine:

Clone this repo:
```bash
git clone https://github.com/OpenGolfSim/meshery-tool.git
cd meshery-tool
```

Setup a python virtual environment:

```bash
python3 -m venv venv
```

Then install the required dependencies:

```bash
./venv/bin/pip install -r requirements.txt
```

#### Building Distributable Apps

We use `pyinstaller` to create app bundles and exe files for windows and macos.

To build:

```bash
pyinstaller meshery.spec
```

#### App Icons

Here's how I created the app icons. First add all the files you need to the iconset folder:

```
Meshery.iconset/icon_16x16@2x.png
Meshery.iconset/icon_32x32.png
Meshery.iconset/icon_32x32@2x.png
Meshery.iconset/icon_64x64.png
Meshery.iconset/icon_64x64@2x.png
Meshery.iconset/icon_128x128.png
Meshery.iconset/icon_128x128@2x.png
Meshery.iconset/icon_256x256.png
Meshery.iconset/icon_256x256@2x.png
Meshery.iconset/icon_512x512.png
Meshery.iconset/icon_512x512@2x.png
```

MacOS has a built-in utility called `iconutil` to create `.icns` files:

```bash
iconutil -c icns images/Meshery.iconset -o images/Meshery.icns
```

To create the windows `ICO` file, you'll need to install the [Imagemagick](https://imagemagick.org/) command-line tool. Take a 256x256 transparent PNG and use it as the input for this command:

```bash
magick images/Meshery.iconset/icon_256x256.png -define icon:auto-resize=16,24,32,48,64,256 images/meshery.ico
```