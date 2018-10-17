
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

  let entrance_port = $('.nodes__table__routing_port').get(0).innerText

  $('.new_frontend__submit').click(ev => {
    let node_id = +$('.new_frontend__node').val();

    let name = $('.new_frontend__name').val();
    let backend_port = +$('.new_frontend__backend_port').val();
    let is_private = $('.new_frontend__is_private').is(':checked');
    let check_ping = $('.new_frontend__check_ping').is(':checked');

    $.ajax('/api/frontend/create', {
      type: "POST",
      data: JSON.stringify({node_id, name, backend_port, is_private, check_ping}),
      contentType: "application/json",
      success: (id) => {
        window.location.reload(true);
      }
    });
  });

  $('.frontends__table').on('click', '.frontends__table__delete', ev => {
    let fnd_row = $(ev.target).parents('tr');
    let id = fnd_row.data('id');

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


  $('.frontends__show_all').click(ev => {
    let target = $(ev.target);

    if (target.text() == 'Показать все') {
      target.text('Скрыть приватные');

      $('.frontends__table__private').removeClass('hide');
    } else {
      target.text('Показать все');

      $('.frontends__table__private').addClass('hide');
    }
  });

  $('.frontends__table').on('click', '.frontends__table__link', ev => {
    let path = $(ev.target).text()

    let url = `http://${window.location.hostname}:${entrance_port}${path}`
    window.location = url
  });


}


function initNodes() {
  $('.new_node__submit').click(ev => {
    let name = $('.new_node__name').val();
    let address = $('.new_node__address').val();
    let routing_port = $('.new_node__routing_port').val();
    let config_port = $('.new_node__config_port').val();

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
    let node_row = $(ev.target).parents('tr');
    let id = node_row.data('id');

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
    let node_row = $(ev.target).parents('tr');
    let id = node_row.data('id');

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
    let target = $(ev.target);

    let from_node = target.data('id');
    let to_node = target.parents('tr').data('id');

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
    let target = $(ev.target);

    let from_node = +target.parents('tr').data('id');
    let to_node = +target.data('id');

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
    let target = $(ev.target);

    let from_node = +target.data('id');    
    let to_node = +target.parents('tr').data('id');

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
    let target = $(ev.target);

    let from_node = +target.parents('tr').data('id');
    let to_node = +target.data('id');

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