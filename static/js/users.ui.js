var UsersUI = (function() {

    return {
        confirmAvatarRemove: function(exp) {
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
