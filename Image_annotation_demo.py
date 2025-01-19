import gradio as gr
from gradio_image_annotation import image_annotator
import codexai.stabi_mets
import datumaro

# example_annotation = {
#     "image": "https://gradio-builds.s3.amazonaws.com/demo-files/base.png",
#     "boxes": [
#         {
#             "xmin": 636,
#             "ymin": 575,
#             "xmax": 801,
#             "ymax": 697,
#             "label": "Vehicle",
#             "color": (255, 0, 0)
#         },
#         {
#             "xmin": 360,
#             "ymin": 615,
#             "xmax": 386,
#             "ymax": 702,
#             "label": "Person",
#             "color": (0, 255, 0)
#         }
#     ]
# }
# 
# examples_crop = [
#     {
#         "image": "https://raw.githubusercontent.com/gradio-app/gradio/main/guides/assets/logo.png",
#         "boxes": [
#             {
#                 "xmin": 30,
#                 "ymin": 70,
#                 "xmax": 530,
#                 "ymax": 500,
#                 "color": (100, 200, 255),
#             }
#         ],
#     },
#     {
#         "image": "https://gradio-builds.s3.amazonaws.com/demo-files/base.png",
#         "boxes": [
#             {
#                 "xmin": 636,
#                 "ymin": 575,
#                 "xmax": 801,
#                 "ymax": 697,
#                 "color": (255, 0, 0),
#             },
#         ],
#     },
# ]


def crop(annotations):
    if annotations["boxes"]:
        box = annotations["boxes"][0]
        return annotations["image"][
            box["ymin"]:box["ymax"],
            box["xmin"]:box["xmax"]
        ]
    return None


def get_boxes_json(image):
    return annotations["boxes"]

# Global handle for current StaBi data
stabi_mets = None	

# Lookup table thumb to full scale image
stabi_full = {}

with gr.Blocks() as demo:
    # Loads a page for a PPN
    def stabi_load_page(evt: gr.SelectData):
        image_thumb = evt.value['image']['url']
        image_default = stabi_full[image_thumb]
        print( "Image selected: %s (%s)" % (image_thumb,image_default) )
        #button_get = gr.Button("Get bounding boxes")
        #json_boxes = gr.JSON()
        #button_get.click(get_boxes_json, annotator, json_boxes)
        return gr.update(
                    value= { "image": stabi_full[evt.value['image']['url']] },
                    #label_list=["Person", "Vehicle"],
                    #label_colors=[(0, 255, 0), (255, 0, 0)],
                    visible=True,
                )

    # Loads a new PPN
    def stabi_load_ppn(ppn):
        print( "Loading PPN %s" % ppn )
        # Load METS file for PPN
        stabi_mets = codexai.stabi_mets.StaBiMets(ppn)
        pages = []
        # Populate page selection dropdown with pages
        for page,images in stabi_mets.iterpages():
            #print( "Page %s, images %s" % (page,str(images)) )
            page_thumb = None
            for image in images:
                page_thumb = stabi_mets.getURLByID(image,'THUMBS')
                if page_thumb is not None: break
            for image in images:
                page_default = stabi_mets.getURLByID(image,'DEFAULT')
                if page_default is not None: break
            if page_thumb is not None and page_default is not None:
                #print( "%s -> %s" % (page,page_image) )
                stabi_full[page_thumb] = page_default
                page_selection = (page_thumb,page)
                pages.append( page_selection )
        #print( pages )
        return gr.Gallery(
            value=pages,
            label="page", 
            show_label=True,
            object_fit="none",
            show_download_button=False,
            allow_preview=False,
            )

    def stabi_previous():
        pass

    def stabi_next():
        pass

    def store_data():
        d = datumaro.DatasetItem(
            )

    #
    # UI
    #
    with gr.Tab("Upload annotation dataset"):
        stabi_uploadformat = gr.Dropdown(
            choices=["COCO","YOLO","Stabi annotate old tool"],
            value="YOLO"
            )
        stabi_upload = gr.UploadButton("Upload annotation dataset", file_count="single")

    with gr.Tab("Select StaBi data"):
        stabi_ppn = gr.Textbox(label="PPN")
        stabi_pages = gr.Gallery()
        stabi_ppn.change(
            stabi_load_ppn, 
            stabi_ppn,
            stabi_pages,
            )
    with gr.Tab("Annotate", id="annotation"):
        stabi_prev = gr.Button(
            value='previous',
            )
        stabi_meaning = gr.Textbox(
            label='meaning',
            info='Enter the meaning of this annotation. For tibetan numerals enter the meaning of the number.',
            )
        stabi_annotator = image_annotator(
            None,
            label_list=['arabic_numeral', 'illustration_image', 'illustration_caption', 'tibetan_page_number','chinese_text','chinese_number','tibetan_content'],
            #label_colors=[(0, 255, 0), (255, 0, 0)],
            visible=False
        )
        stabi_nxt = gr.Button(
            value='next',
            )
        stabi_pages.select(
            stabi_load_page,
            None, #stabi_pages,
            stabi_annotator,
            )
        #button_get = gr.Button("Get bounding boxes")
        #json_boxes = gr.JSON()
        #button_get.click(get_boxes_json, annotator, json_boxes)
    with gr.Tab("Download", id="download"):
        stabi_downloadformat = gr.Dropdown(
            choices=["COCO","YOLO"],
            value="YOLO"
            )
        stabi_download = gr.DownloadButton("Download annotation information")

    if __name__ == "__main__":
        demo.launch()

# vim:expandtab
