function on_click_image_in_eagle_gly(e){
    let _src = e.currentTarget.src;
    let _txt = gradioApp().querySelector('#txt_eagle_trans > label > textarea');
    _txt.value = _src;
    _txt.dispatchEvent(new Event("input", { bubbles: true }));
}

// gallery
onUiUpdate(function () {
    let _txt = gradioApp().querySelector('#txt_eagle_trans > label > textarea');
    if (_txt == null) return;

    let gallery_items = gradioApp().querySelectorAll('.gallery-item > img');
	gallery_items.forEach(function(item){
        item.addEventListener('click', on_click_image_in_eagle_gly, true);
	});
});
