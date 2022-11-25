import os
import glob
import io
import requests

from PIL import Image
import gradio as gr

from modules import script_callbacks, extras, ui, generation_parameters_copypaste

from scripts.eagleapi.application import info
from scripts.eagleapi.item import addFromPaths

DEBUG = False

#
# UI callback
#
def on_ui_tabs():
    with gr.Blocks() as main_block:
        with gr.Column():
            with gr.Row():
                with gr.Column(scale=1):
                    btn_send_to_eagle = gr.Button("Send image(s) to Eagle", variant="primary")
                with gr.Column(scale=3):
                    html_current_status = gr.HTML(label="Current Status")
            with gr.Row():
                with gr.Column(scale=1):
                    btn_load_images = gr.Button("Load images")
                    gr.HTML("<H1>UI/Load Settings</H1>")
                    with gr.Group():
                        chk_search_image_file_recursive = gr.Checkbox(label="Search image file recursively")
                        chk_show_searched_images = gr.Checkbox(label="Show searched images in gallery")
                    gr.HTML("<H1>Output Settings</H1>")
                    with gr.Group():
                        # specify Eagle folderID
                        txt_save_to_eagle_folderid = gr.Text(label="FolderID on Eagle (option)")
                        # flg: save generation info to annotation
                        chk_save_generationinfo_to_eagle_as_annotation = gr.Checkbox(value=True, label="Save Generation info as Annotation")
                        # flg: save positive prompt to tags
                        chk_save_positive_prompt_to_eagle_as_tags = gr.Checkbox(value=True, label="Save positive prompt to Eagle as tags")
                        # radio: save negative prompt to tags or "n:"
                        radio_save_negative_prompt_to_eagle_as = gr.Radio(label="Save negative prompt to Eagle as,", choices=["None", "tag", "n:tag"], value="n:tag", type="value")

                    with gr.Group():
                        # Hidden items
                        hidden_txt = gr.Text(visible=DEBUG, elem_id="txt_eagle_trans")
                        hidden_img = gr.Image(type="pil", elem_id="img_eagle_trans", interactive=False)

                with gr.Column(scale=3):
                    txt_target_images_dir = gr.Text(label="Target Images Directory (full path)")
                    html_1 = gr.HTML()
                    txtarea_generation_info = gr.TextArea(label="Generation Info")
                    html_2 = gr.HTML(visible=False)
                    with gr.Row():
                        num_pagenation = gr.Number(label="Page No", precision=0, value=1)
                        html_max_pagenation = gr.HTML()
                        slider_gallery_image_max = gr.Slider(label="Image Max Num in 1 Page", minimum=1, step=1, value=30)
                    gly_loaded_images = gr.Gallery(label="Target Images", elem_id="gly_eagle_trans").style(grid=6)

        #
        def _get_images(target_dir, flg_recursive, page_num=1, image_per_page=None):
            if flg_recursive:
                _glob_pattern = ""f"{target_dir}/**/*.png"
            else:
                _glob_pattern = ""f"{target_dir}/*.png"
            _images = [p for p in glob.glob(_glob_pattern, recursive=True) if os.path.isfile(p)]
            if image_per_page:
                _from = image_per_page*(page_num-1)
                _to = min(image_per_page*page_num, len(_images))
                return _images[_from:_to], len(_images)
            else:
                return _images, len(_images)

        #
        # Events (load images)
        #
        def load_images(
            txt_target_images_dir,
            chk_search_image_file_recursive,
            num_pagenation,
            slider_gallery_image_max,
            chk_show_searched_images):

            # dir check
            if not os.path.exists(txt_target_images_dir):
                _error = "Error: target image path is not exist."
                print(_error)
                return [gr.update(value=f"<div>{_error}</div>"), gr.update(value=None), gr.update(), gr.update(value=None), gr.update(value=None)]
            elif not os.path.isdir(txt_target_images_dir):
                _error = "Error: target image path is not directory."
                print(_error)
                return [gr.update(value=f"<div>{_error}</div>"), gr.update(value=None), gr.update(), gr.update(value=None), gr.update(value=None)]
            else:
                _images, _len_images = _get_images(txt_target_images_dir, chk_search_image_file_recursive, num_pagenation, slider_gallery_image_max)
                _mes = f"{_len_images} images found."
                _image_for_info = None if len(_images) == 0 else _images[0]
                if not chk_show_searched_images:
                    _images = None
                _page_max = -(-_len_images//slider_gallery_image_max)
                _page = min(num_pagenation, _page_max)
                return [
                    gr.update(value=_mes),
                    gr.update(value=_images),
                    gr.update(value=_page),
                    gr.update(value=_image_for_info),
                    gr.update(value=f"<p> / {_page_max} page total.</p>")
                    ]

        def on_click_btn_load_images(txt_target_images_dir, chk_search_image_file_recursive, num_pagenation, slider_gallery_image_max, chk_show_searched_images):
            return load_images(txt_target_images_dir, chk_search_image_file_recursive, 1, slider_gallery_image_max, chk_show_searched_images)

        btn_load_images.click(
            fn=on_click_btn_load_images,
            inputs=[
                txt_target_images_dir,
                chk_search_image_file_recursive,
                num_pagenation,
                slider_gallery_image_max,
                chk_show_searched_images],
            outputs=[
                html_current_status,
                gly_loaded_images,
                num_pagenation,
                hidden_img,
                html_max_pagenation]
        )

        def on_change_slider_pagenation(txt_target_images_dir, chk_search_image_file_recursive, num_pagenation, slider_gallery_image_max, chk_show_searched_images):
            return load_images(txt_target_images_dir, chk_search_image_file_recursive, num_pagenation, slider_gallery_image_max, chk_show_searched_images)

        num_pagenation.change(
            fn=on_change_slider_pagenation,
            inputs=[
                txt_target_images_dir,
                chk_search_image_file_recursive,
                num_pagenation,
                slider_gallery_image_max,
                chk_show_searched_images],
            outputs=[
                html_current_status,
                gly_loaded_images,
                num_pagenation,
                hidden_img,
                html_max_pagenation]
        )

        def on_change_hidden_txt(txt_target_images_dir, hidden_txt):
            if hidden_txt and hidden_txt !="" and os.path.exists(hidden_txt):
                _filename = os.path.splitext(os.path.basename(hidden_txt))[0] + ".png"  # filename. no ext
                _filepath = os.path.join(txt_target_images_dir, _filename)
                return gr.update(value=_filepath)
            elif "http" in hidden_txt:
                _img = Image.open(io.BytesIO(requests.get(hidden_txt).content))
                return gr.update(value=_img)
            else:
                return None
        hidden_txt.change(
            fn=on_change_hidden_txt,
            inputs=[txt_target_images_dir, hidden_txt],
            outputs=[hidden_img]
        )
        hidden_img.change(
            fn=ui.wrap_gradio_call(extras.run_pnginfo),
            inputs=[hidden_img],
            outputs=[html_1, txtarea_generation_info, html_2],
        )

        #
        # Events (send images)
        #
        def _get_EAGLE_ITEM_list(
            _image_paths,
            chk_save_generationinfo_to_eagle_as_annotation,
            chk_save_positive_prompt_to_eagle_as_tags,
            radio_save_negative_prompt_to_eagle_as
            ):
            _ret_eagle_list = []

            for _img_path in _image_paths:
                # collect info
                fullfn = _img_path
                filename = os.path.splitext(os.path.basename(_img_path))[0]
                image = Image.open(fullfn)
                items = image.info
                info = items.get('parameters', '')
                params = generation_parameters_copypaste.parse_generation_parameters(info)
                #
                pos_prompt = params["Prompt"]
                neg_prompt = params["Negative prompt"]
                #
                annotation = None
                tags = []
                if chk_save_generationinfo_to_eagle_as_annotation:
                    annotation = info
                if chk_save_positive_prompt_to_eagle_as_tags:
                    tags += [ x.strip() for x in pos_prompt.split(",") if x.strip() != "" ]
                if radio_save_negative_prompt_to_eagle_as == "tag":
                    tags += [ x.strip() for x in neg_prompt.split(",") if x.strip() != "" ]
                elif radio_save_negative_prompt_to_eagle_as == "n:tag":
                    tags += [ f"n:{x.strip()}" for x in neg_prompt.split(",") if x.strip() != "" ]
                _ret_eagle_list.append(addFromPaths.EAGLE_ITEM(filefullpath=fullfn, filename=filename, website="", tags=tags, annotation=annotation))

            return _ret_eagle_list

        def on_click_btn_send_to_eagle(
            chk_search_image_file_recursive, txt_target_images_dir,
            chk_save_generationinfo_to_eagle_as_annotation, chk_save_positive_prompt_to_eagle_as_tags,
            radio_save_negative_prompt_to_eagle_as, txt_save_to_eagle_folderid):
            # check Eagle
            _ret = info.info()
            try:
                _ret.raise_for_status()
            except Exception as e:
                _error_mes = "ERROR: Eagle-API.application.info failed.\nmake sure Eagle application is running.\nSending Canceled."
                print(_error_mes)
                print(e)
                print(_ret.status_code)
                return [gr.update(value=_error_mes)]

            _images, _len = _get_images(txt_target_images_dir, chk_search_image_file_recursive)
            _params = _get_EAGLE_ITEM_list(
                _images, chk_save_generationinfo_to_eagle_as_annotation,
                chk_save_positive_prompt_to_eagle_as_tags, radio_save_negative_prompt_to_eagle_as)
            _ret = addFromPaths.add_from_paths(_params, step=10, folderId=txt_save_to_eagle_folderid)
            _ret_html = ""
            for x in _ret:
                _ret_html += f"<div>{x}</div>"
            return [gr.update(value=_ret_html)]
        btn_send_to_eagle.click(
            fn=on_click_btn_send_to_eagle,
            inputs=[chk_search_image_file_recursive, txt_target_images_dir,
                    chk_save_generationinfo_to_eagle_as_annotation, chk_save_positive_prompt_to_eagle_as_tags,
                    radio_save_negative_prompt_to_eagle_as, txt_save_to_eagle_folderid],
            outputs=[html_current_status]
        )

    # return required as (gradio_component, title, elem_id)
    return (main_block, "Eagle Transfer Board", "eagle_transfer_board"),

# on_UI
script_callbacks.on_ui_tabs(on_ui_tabs)
