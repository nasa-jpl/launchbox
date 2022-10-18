function changeView(hash) {
  // Params
  var parts = hash.split('?')
  var view = parts[0].replace('#', '')
  // Arg: Parse
  var args = {}
  var pairs = (parts.length > 1) ? parts[1].split('&') : []
  for (var index in pairs) {
    var pair = pairs[index].split('=')
    args[pair[0]] = pair[1]
  }
  // Arg: Values
  var arg_id = ('id' in args) ? args['id'] : false
  var arg_error = ('error' in args) ? args['error'] : false
  var arg_modal = ('modal' in args) ? args['modal'] : false
  var arg_subview = ('subview' in args) ? args['subview'] : false
  // Menu
  document.querySelectorAll('#sidebar_menu a').forEach(function(menu_item) {
    menu_item.classList.toggle('current', (menu_item.hash == `#${view}`))
  })
  // Modals
  document.querySelectorAll('.modal').forEach(function(modal) {
    modal.remove()
  })
  // Views
  document.querySelectorAll('.appview').forEach(function(appview) {
    appview.classList.add('hidden')
    appview.querySelectorAll('.subview').forEach(function(subview) {
      subview.classList.add('hidden')
    })
    appview.removeAttribute('data-id')
  })
  // Submenus
  document.querySelectorAll('.submenu').forEach(function(submenu) {
    submenu.querySelectorAll('.tab').forEach(function(tab) {
      tab.classList.remove('current')
    })
  })
  // Elements
  var view_elem = document.querySelector(`.appview[view=${view}]`)
  var subview_elem = (view_elem) ? view_elem.querySelector(`.subview[name=${arg_subview}`) : false
  var submenu_elem = (view_elem) ? view_elem.querySelector(`.submenu[view=${view}]`) : false
  var tab_elem = (submenu_elem) ? submenu_elem.querySelector(`.tab[subview=${arg_subview}]`) : false
  var tab_default_elem = (submenu_elem) ? submenu_elem.querySelector('.tab.default') : false
  // View
  if (view_elem) {
    view_elem.classList.remove('hidden')
    if (arg_id) {
      view_elem.setAttribute('data-id', arg_id)
    }
    // Subviews
    if (subview_elem) {
      subview_elem.classList.remove('hidden')
    }
    // Submenu
    if (tab_elem) {
      tab_elem.classList.add('current')
    } else if (tab_default_elem) {
      tab_default_elem.click()
      return
    }
  }
  // Error
  if (arg_error) {
    var errors = {
      'credentials': 'Please enter valid credentials.',
      'database': 'Unknown error.',
      'username-exists': 'Provided username already exists.',
      'username-invalid': 'Usernames may only contain letters, numbers and dashes.'
    }
    if (arg_error in errors) {
      setTimeout(function() {
        alert(errors[arg_error])
      }, 100)
    }
  }
  // Special
  LBUtil.poll.reset()
  if (view == 'deploys') {
    getDeploys()
    LBUtil.poll.start(getDeploys, 10000)
  } else if (view == 'deploy') {
    if (arg_id) {
      getDeployDetails(arg_id)
      LBUtil.poll.start(function() {
        getDeployDetails(arg_id)
      }, 5000)
    }
  } else if (view == 'sites') {
    getSites()
    if (arg_modal == 'add-site') {
      addSiteModal()
    }
  } else if (view == 'site') {
    if (arg_id) {
      getSiteDetails(arg_id)
    }
  } else if (view == 'services') {
    getServices()
    if (arg_modal == 'add-service') {
      addServiceModal()
    }
  } else if (view == 'service') {
    if (arg_id) {
      getServiceDetails(arg_id)
    }
  } else if (view == 'monitoring') {
    getStats()
  }
}

function changeSubview(view, subview) {
  args = []
  var elem = document.querySelector(`.appview[view=${view}]`)
  if (elem.hasAttribute('data-id')) {
    args.push(`id=${elem.getAttribute('data-id')}`)
  }
  args.push(`subview=${subview}`)
  window.location.hash = `#${view}?${args.join("&")}`
}

function changeHash(hash) {
  getAuth(function(user) {
    if (user) {
      if (hash.startsWith("#auth")) {
        window.location.hash = "#sites"
      } else {
        changeView(hash)
      }
    } else {
      if (hash.startsWith("#auth") || hash.startsWith("#register")) {
        changeView(hash)
      } else {
        window.location.hash = "#auth"
      }
    }
  })
}
