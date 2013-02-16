var UsersUI = (function() {

    return {
        avatarChange: function(userid) {
            return $(
'<div class="modal hide fade">' +
    '<div class="modal-header">' +
        '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
        '<h3>Change avatar</h3>' +
    '</div>' +
    '<div class="modal-body">' +
        '<form id="user_avatar" class="form-horizontal" enctype="multipart/form-data">' +
        '<div class="fileupload fileupload-new" data-provides="fileupload">' +
            '<input id="id" type="hidden" name="id" value="' + userid + '" />' +
            '<div>' +
                '<span class="btn btn-file"><span class="fileupload-new">Select image</span><span class="fileupload-exists">Change</span><input id="avatar" name="avatar" type="file" /></span>' +
                '<a href="#" class="btn fileupload-exists" data-dismiss="fileupload">Remove</a>' +
            '</div>' +
            '<br />' +
            '<div class="fileupload-new thumbnail" style="width: 300px; height: 300px;"><img src="http://www.placehold.it/300x300/EFEFEF/AAAAAA&text=no+image" /></div>' +
            '<div class="fileupload-preview fileupload-exists thumbnail" style="max-width: 300px; max-height: 300px; line-height: 20px;"></div>' +
        '</div>' +
        '</form>' +
    '</div>' +
    '<div class="modal-footer">' +
        '<a href="#" class="btn btn-danger" data-dismiss="modal">Done</a>' +
    '</div>' +
'</div>'
                ).modal();
        },

        confirmAvatarRemove: function() {
            return $(
'<div class="modal hide fade">' +
  '<div class="modal-header">' +
    '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>' +
    '<h3>Remove avatar</h3>' +
  '</div>' +
  '<div class="modal-body">' +
    '<p>Do you really want to proceed?</p>' +
  '</div>' +
  '<div class="modal-footer">' +
    '<a href="#" class="btn btn-danger" data-dismiss="modal">Continue</a>' +
  '</div>' +
'</div>'
            ).modal();
        },
    };
}());
