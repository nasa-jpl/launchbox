var auth = false
var interval = false

function addService() {
  var button = document.querySelector('#add-service-button')
  var service_id = document.querySelector('.modal[name=add-service] input[name=service_id]').value
  var name = document.querySelector('.modal[name=add-service] input[name=name]').value
  var provider_id = document.querySelector('.modal[name=add-service] select[name=provider_id]').value
  var repo_url = document.querySelector('.modal[name=add-service] input[name=repo_url]').value
  var branch = document.querySelector('.modal[name=add-service] input[name=branch]').value
  var env_name = document.querySelector('.modal[name=add-service] input[name=env_name]').value
  if (service_id.length == 0) {
    alert('Please enter a service identifier.')
    return
  }
  if (name.length == 0) {
    alert('Please enter a service name.')
    return
  }
  if (provider_id.length == 0) {
    alert('Please select a provider.')
    return
  }
  if (repo_url.length == 0) {
    alert('Please enter a repo URL.')
    return
  }
  if (branch.length == 0) {
    alert('Please enter a branch name.')
    return
  }
  if (env_name.length == 0) {
    alert('Please enter an environment name.')
    return
  }
  // Interface
  button.disabled = true
  button.innerHTML = 'Creating...'
  // Request
  LBAPI.services.add(service_id, name, provider_id, repo_url, branch, env_name, function(result) {
    if (result.valid()) {
      window.location.hash = '#services'
    } else {
      alert('API Error: Unable to create service.')
    }
  })
}

function addSite() {
  var button = document.querySelector('#add-site-button')
  var site_id = document.querySelector('.modal[name=add-site] input[name=site_id]').value
  var service_id = document.querySelector('.modal[name=add-site] select[name=service_id]').value
  if (site_id.length == 0) {
    alert('Please enter a site identifier.')
    return
  }
  if (service_id.length == 0) {
    alert('Please select a service.')
    return
  }
  // Interface
  button.disabled = true
  button.innerHTML = 'Creating...'
  // Request
  LBAPI.sites.add(site_id, service_id, function(result) {
    if (result.valid()) {
      window.location.hash = '#sites'
    } else {
      alert('API Error: Unable to create site.')
    }
  })
}

function addServiceModal() {
  document.querySelector('.appview[view=services]').innerHTML += addServiceModalView()
  // Events
  document.querySelector('.modal').addEventListener('click', function(e) {
    if (event.target.closest('.modal-body')) return;
    window.location.hash = '#services'
  })
  document.querySelector('#add-service-button').addEventListener('click', function() {
    addService()
  })
}

function addSiteModal() {
  LBAPI.services.list(function(result) {
    if (result.valid()) {
      // Params
      var services = result.data['services']
      document.querySelector('.appview[view=sites]').innerHTML += addSiteModalView(services)
      // Events
      document.querySelector('.modal').addEventListener('click', function(e) {
        if (event.target.closest('.modal-body')) return;
        window.location.hash = '#sites'
      })
      document.querySelector('#add-site-button').addEventListener('click', function() {
        addSite()
      })
    }
  })
}

function getAPI() {
  LBAPI.status(function(result) {
    if (result.valid()) {
      // Params
      var data = result.data
      var env = data['env']
      var root = data['root']
      var version = data['version']
      // Interface
      var html = `${LBUI.format.capitalize(env)} - ${LBUI.format.text.light(root)}`
      document.querySelector('#env_data').innerHTML = html
    }
  })
}

function getAuth(callback) {
  if (auth) {
    callback(auth)
  } else {
    LBAPI.auth.state(function(result) {
      if (result.valid()) {
        auth = result.data['user']
        // Interface
        if (auth) {
          document.querySelector('#user_state').innerHTML = `
            <div class="font-semibold text-lg text-gray-200">
              @${auth.user_id}
            </div>
            <hr class="mx-2 my-1 border-indigo-600">
            <a href="/api/auth/logout" class="text-indigo-300">
              <div class="font-bold text-lg">
                Logout
              </div>
            </a>
          `
          document.querySelector('#user_state').classList.remove('hidden')
        } else {
          document.querySelector('#user_state').classList.add('hidden')
        }
        // Callback
        callback(auth)
      }
    })
  }
}

function getDeploys() {
  LBAPI.deploys.list(function(result) {
    if (result.valid()) {
      // Params
      var deploys = result.data['deploys']
      // List
      var target = document.querySelector('.appview[view=deploys] .view[name=list]')
      target.innerHTML = createDeploysView(deploys)
    }
  })
}

function getDeployDetails(deploy_id) {
  // Elements
  var subview_service = document.querySelector('.appview[view=deploy] .subview[name=service]')
  // Reset
  subview_service.innerHTML = ''
  // Heading
  document.querySelector('.appview[view=deploy] .submenu .left').innerHTML = `
    <span class="text-gray-700">Deploy:</span> <span class="font-bold">${deploy_id}</span>
  `
  document.querySelector('.appview[view=deploy] .submenu .right').innerHTML = ''
  // Request
  LBAPI.deploys.get(deploy_id, function(result) {
    if (result.valid()) {
      // Params
      var deploy = result.data['deploy']
      var service_id = deploy['service_id']
      // Heading
      document.querySelector('.appview[view=deploy] .submenu .right').innerHTML = `
        Service: <a href="#service?id=${service_id}">${LBUI.format.badge('main', service_id)}</a>
      `
      // Overview
      subview_service.innerHTML = createDeployServicePanel(deploy)
    }
  })
}

function getServices() {
  LBAPI.services.list(function(result) {
    if (result.valid()) {
      // Params
      var services = result.data['services']
      // List
      var target = document.querySelector('.appview[view=services] .view[name=list]')
      target.innerHTML = createServicesView(services)
    }
  })
}

function getSites() {
  LBAPI.sites.list(function(result) {
    if (result.valid()) {
      var sites = result.data['sites']
      // List
      var target = document.querySelector('.appview[view=sites] .view[name=list]')
      target.innerHTML = createSitesView(sites)
    }
  })
}

function getSiteDetails(site_id) {
  // Elements
  var subview_hostnames = document.querySelector('.appview[view=site] .subview[name=hostnames]')
  var subview_notes = document.querySelector('.appview[view=site] .subview[name=notes]')
  var subview_resources = document.querySelector('.appview[view=site] .subview[name=resources]')
  var subview_events = document.querySelector('.appview[view=site] .subview[name=events]')
  var subview_manage = document.querySelector('.appview[view=site] .subview[name=manage]')
  // Reset
  subview_hostnames.innerHTML = ''
  subview_notes.innerHTML = ''
  subview_resources.innerHTML = ''
  subview_events.innerHTML = ''
  subview_manage.innerHTML = ''
  // Heading
  document.querySelector('#site_title').innerHTML = `
    <span class="text-gray-700">Site:</span> <span class="font-bold">${site_id}</span>
  `
  // Request
  LBAPI.sites.get(site_id, function(result) {
    if (result.valid()) {
      // Params
      var site = result.data['site']
      // Hostnames
      var hostnames = site['hostnames']
      subview_hostnames.innerHTML = createSiteHostnamesPanel(site_id, hostnames)
      // Notes
      var notes = site['notes']
      subview_notes.innerHTML = createSiteNotesPanel(site_id, notes)
      // Resources
      var deployment = site['deployment']
      subview_resources.innerHTML = createSiteResourcesPanel(site_id, deployment)
      // Events
      var events = site['events']
      subview_events.innerHTML = createSiteEventsPanel(site_id, events)
      // Manage
      subview_manage.innerHTML = createSiteManagePanel(site_id)
      // Interface: Events
      siteDetailEvents(site_id)
    }
  })
}

function siteDetailEvents(site_id) {
  // Events: [add-hostname-button]
  document.getElementById('add-hostname-button').addEventListener('click', function(e) {
    addHostname(site_id, e.target)
  })
  // Events: [primary-hostname-button]
  document.querySelectorAll('.primary-hostname-button').forEach(function(elem) {
    elem.addEventListener('click', function(e) {
      primaryHostname(site_id, e.target)
    })
  })
  // Events: [remove-hostname-button]
  document.querySelectorAll('.remove-hostname-button').forEach(function(elem) {
    elem.addEventListener('click', function(e) {
      removeHostname(site_id, e.target)
    })
  })
  // Events: [add-note-button]
  document.getElementById('add-note-button').addEventListener('click', function(e) {
    addNote(site_id)
  })
  // Events: [add-note-input]
  document.getElementById('add-note-input').addEventListener('keyup', function(e) {
    if (e.key == 'Enter') {
      addNote(site_id)
    }
  })
  // Events: [export-site-button]
  document.querySelectorAll('#export-site-button').forEach(function(elem) {
    elem.addEventListener('click', function(e) {
      exportSite(site_id, e.target)
    })
  })
  // Events: [remove-site-button]
  document.querySelectorAll('#reset-site-button').forEach(function(elem) {
    elem.addEventListener('click', function(e) {
      resetSite(site_id, e.target)
    })
  })
  // Events: [remove-site-button]
  document.querySelectorAll('#remove-site-button').forEach(function(elem) {
    elem.addEventListener('click', function(e) {
      removeSite(site_id, e.target)
    })
  })
}

function getServiceDetails(service_id) {
  // Elements
  var subview_deployments = document.querySelector('.appview[view=service] .subview[name=deploys]')
  // Reset
  subview_deployments.innerHTML = ''
  // Heading
  document.querySelector('#service_title').innerHTML = '<span class="text-gray-700">Loading...</span>'
  // Request
  LBAPI.services.get(service_id, function(result) {
    if (result.valid()) {
      // Params
      var service = result.data['service']
      // Heading
      document.querySelector('#service_title').innerHTML = `
        <span class="text-gray-700">Service:</span> <span class="font-bold">${service_id}</span>
      `
      // Deployments
      var commits = service['commits']
      var deployments = service['deployments']
      subview_deployments.innerHTML = createServiceDeploymentsPanel(service_id, commits, deployments)
    }
    // Events
    serviceDetailEvents(service_id)
  })
}

function serviceDetailEvents(service_id) {
  // Events: [deploy-service-button]
  document.querySelectorAll('.deploy-service-button').forEach(function(elem) {
    elem.addEventListener('click', function(e) {
      deployService(service_id, e.target)
    })
  })
}

function getStats() {
  // Interface
  var detailed = document.querySelector('.appview[view=monitoring] .subview[name=detailed]')
  var overview = document.querySelector('.appview[view=monitoring] .subview[name=overview]')
  // Reset
  detailed.innerHTML = ''
  overview.innerHTML = ''
  // Request
  LBAPI.stats.latest(function(result) {
    if (result.valid()) {
      // Params
      var latest = result.data['latest']
      // Bar
      var bar = `
        
      `
      // Render
      var detailed_html = createStatsTitleBar(Object.keys(latest).length)
      var overview_html = createStatsTitleBar(Object.keys(latest).length)
      for (var source in latest) {
        var data = latest[source]
        detailed_html += createStatsDetailedRow(source, data)
        overview_html += createStatsOverviewRow(source, data)
      }
      detailed.innerHTML = detailed_html
      overview.innerHTML = overview_html
      // Events: [monitor-reload]
      document.querySelector('#monitor_reload').addEventListener('click', function() {
        getStats()
      })
    }
  })
}

function deployService(service_id, target) {
  // Params
  var commit_sha = target.getAttribute('data-commit-sha')
  console.log(commit_sha)
  // Interface
  target.disabled = true
  target.innerText = '...'
  // Request
  LBAPI.services.deploy(service_id, commit_sha, function(result) {
    if (result.valid()) {
      getServiceDetails(service_id)
    }
  })
}

function exportSite(site_id, target) {
  // Interface
  target.disabled = true
  target.innerText = 'Exporting...'
  // Request
  LBAPI.sites.export(site_id, function(result) {
    if (result.valid()) {
      // Params
      var data = result.data
      var blob = new Blob(data, {'type': 'application/json'})
      var url = window.URL.createObjectURL(blob)
      // Download
      var link = document.createElement('a')
      link.download = `${site_id}-export.json`
      link.href = `/api/sites/${site_id}/content`
      document.body.appendChild(link)
      link.click()
      // Interface
      target.innerText = 'Downloading...'
      // Cleanup
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      // Restore
      setTimeout(function() {
        target.innerText = 'Download'
        target.disabled = false
      }, 4000)
    }
  })
}

function removeSite(site_id, target) {
  // Confirm
  if (confirm(`Are you sure you want to delete site: ${site_id}?`)) {
    // Interface
    target.disabled = true
    target.innerText = 'Deleting...'
    // Request
    LBAPI.sites.remove(site_id, function(result) {
      if (result.valid()) {
        window.location.hash = '#sites'
      }
    })
  }
}

function resetSite(site_id, target) {
  // Confirm
  if (confirm(`Are you sure you want to reset the database (remove all content/data) for site: ${site_id}?`)) {
    // Interface
    target.disabled = true
    target.innerText = 'Resetting...'
    // Request
    LBAPI.sites.reset_db(site_id, function(result) {
      if (result.valid()) {
        getSiteDetails(site_id)
        alert(`Database reset for site: ${site_id}`)
      }
    })
  }
}

function updateSiteAttr(site_id, attr, value, target) {
  // Interface
  target.disabled = true
  target.innerText = 'Saving...'
  // Request
  LBAPI.sites.update(site_id, attr, value, function(result) {
    if (result.valid()) {
      getSites()
      getSiteDetails(site_id)
    }
  })
}

function addHostname(site_id, target) {
  // Params
  var hostname = document.getElementById('add-hostname-input').value
  // Check
  if (hostname.length > 0) {
    // Interface
    target.disabled = true
    target.innerText = "Adding..."
    // Request
    LBAPI.sites.hostnames.add(site_id, hostname, function(result) {
      if (result.valid()) {
        getSites()
        getSiteDetails(site_id)
      }
    })
  } else {
    alert("Please enter a hostname.")
  }
}

function primaryHostname(site_id, target) {
  // Params
  var hostname = target.getAttribute('data-hostname')
  // Interface
  target.disabled = true
  target.innerText = 'Updating...'
  // Request
  LBAPI.sites.hostnames.primary(site_id, hostname, function(result) {
    if (result.valid()) {
      getSiteDetails(site_id)
    }
  })
}

function removeHostname(site_id, target) {
  // Params
  var hostname = target.getAttribute('data-hostname')
  // Confirm
  if (confirm(`Are you sure you want to delete hostname: ${hostname}?`)) {
    // Interface
    target.disabled = true
    target.innerText = 'Removing...'
    // Request
    LBAPI.sites.hostnames.remove(site_id, hostname, function(result) {
      if (result.valid()) {
        getSiteDetails(site_id)
      }
    })
  }
}

function addNote(site_id) {
  // Interface
  var button = document.getElementById('add-note-button')
  var input = document.getElementById('add-note-input')
  // Params
  var text = input.value
  // Check
  if (text.length > 0) {
    // Interface
    button.disabled = true
    button.innerText = 'Adding note...'
    // Request
    LBAPI.sites.notes.add(site_id, text, function(result) {
      if (result.valid()) {
        getSiteDetails(site_id)
      }
    })
  } else {
    alert('Please enter a note.')
  }
}

function setupUI() {
  // Listeners
  document.querySelectorAll('.submenu').forEach(function(submenu) {
    var view = submenu.getAttribute('view')
    submenu.querySelectorAll('div.tab').forEach(function(tab) {
      var subview = tab.getAttribute('subview')
      tab.addEventListener('click', function() {
        changeSubview(view, subview)
      })
    })
  })
  window.addEventListener("hashchange", function() {
    changeHash(window.location.hash)
  })
  // Interface
  getAPI()
}

function startUI() {
  changeHash(window.location.hash || '#sites')
}

setupUI()
startUI()
