
$.ajaxSetup({
  error: (jqXHR) => {
    alert(`Status: ${jqXHR.status}\n${jqXHR.responseText}`)
  }
});

$(function () {
    initFrontends();
    initNodes();
});


function initFrontends() {
  $('.new_frontend__submit').click(ev => {
    node_id = +$('.new_frontend__node').val();
    routing_path = $('.new_frontend__routing_path').val();
    backend_path = $('.new_frontend__backend_path').val();
    backend_port = $('.new_frontend__backend_port').val();
    is_private = $('.new_frontend__is_private').is(':checked');
    check_ping = $('.new_frontend__check_ping').is(':checked');

    $.ajax('/api/frontend/create', {
      type: "POST",
      data: JSON.stringify({node_id, routing_path, backend_path, backend_port, is_private, check_ping}),
      contentType: "application/json",
      success: (id) => {
        window.location.reload(true);
      }
    });
  });

  $('.frontends__table').on('click', '.frontends__table__delete', ev => {
    fnd_row = $(ev.target).parents('tr');
    id = fnd_row.data('id');

    $.ajax('/api/frontend/delete', {
      type: "DELETE",
      data: JSON.stringify({id}),
      contentType: "application/json",
      success: () => {
        //fnd_row.remove();
        window.location.reload(true);
      }
    });
  });
}


function initNodes() {
  $('.new_node__submit').click(ev => {
    name = $('.new_node__name').val();
    address = $('.new_node__address').val();
    routing_port = $('.new_node__routing_port').val();
    config_port = $('.new_node__config_port').val();

    $.ajax('/api/node/create', {
      type: "POST",
      data: JSON.stringify({name, address, routing_port, config_port}),
      contentType: "application/json",
      success: (id) => {
        window.location.reload(true);
      }
    });
  });


  $('.nodes__table').on('click', '.nodes__table__update', ev => {
    node_row = $(ev.target).parents('tr');
    id = node_row.data('id');

    $.ajax('/api/node/update_config', {
      type: "POST",
      data: JSON.stringify({id}),
      contentType: "application/json",
      success: () => {
        //node_row.remove();
        alert('OK')
      }
    });
  });


  $('.nodes__table').on('click', '.nodes__table__delete', ev => {
    node_row = $(ev.target).parents('tr');
    id = node_row.data('id');

    $.ajax('/api/node/delete', {
      type: "DELETE",
      data: JSON.stringify({id}),
      contentType: "application/json",
      success: () => {
        //node_row.remove();
        window.location.reload(true);
      }
    });
  });


  // VVVV edge api VVVV
  $('.nodes__table').on('click', '.nodes__table__add_parent', ev => {
    target = $(ev.target);

    from_node = target.data('id');
    to_node = target.parents('tr').data('id');

    $.ajax('/api/edge/create', {
      type: "POST",
      data: JSON.stringify({from_node, to_node}),
      contentType: "application/json",
      success: () => {
        window.location.reload(true);
      }
    });
  });

  $('.nodes__table').on('click', '.nodes__table__add_child', ev => {
    target = $(ev.target);

    from_node = +target.parents('tr').data('id');
    to_node = +target.data('id');

    $.ajax('/api/edge/create', {
      type: "POST",
      data: JSON.stringify({from_node, to_node}),
      contentType: "application/json",
      success: () => {
        window.location.reload(true);
      }
    });
  });


  $('.nodes__table').on('click', '.nodes__table__delete_parent', ev => {
    target = $(ev.target);

    from_node = +target.data('id');    
    to_node = +target.parents('tr').data('id');

    $.ajax('/api/edge/delete', {
      type: "DELETE",
      data: JSON.stringify({from_node, to_node}),
      contentType: "application/json",
      success: () => {
        //target.parent().parent().parent().remove();
        window.location.reload(true);
      }
    });
  });

  $('.nodes__table').on('click', '.nodes__table__delete_child', ev => {
    target = $(ev.target);

    from_node = +target.parents('tr').data('id');
    to_node = +target.data('id');

    $.ajax('/api/edge/delete', {
      type: "DELETE",
      data: JSON.stringify({from_node, to_node}),
      contentType: "application/json",
      success: () => {
        //target.parent().parent().parent().remove();
        window.location.reload(true);
      }
    });
  });
}