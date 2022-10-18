function addServiceModalView() {
  var html = `
    <div class="modal" name="add-service" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="modal-bg"></div>
      <div class="modal-view">
        <div class="modal-frame">
          <div class="modal-body">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="modal-title" id="modal-title">New Service</h3>
              <div class="mt-4">
                <label for="service_id">Service Identifier</label>
                <div class="mt-1">
                  <input type="text" name="service_id" placeholder="example-service">
                </div>
                <p class="mt-2 mb-4 text-sm text-gray-500">
                  Service identifiers are used are used internal as a unique identifier.
                  <b>Allowed characters</b>: letters, numbers and dashes.
                </p>
              </div>
              <div class="mt-4">
                <label for="name">Service Name</label>
                <div class="mt-1">
                  <input type="text" name="name" placeholder="Example Service">
                </div>
              </div>
              <div class="mt-4">
                <label for="provider_id">Provider</label>
                <div class="mt-1">
                  <select name="provider_id">
                    <option value="github" selected>Github (github.com)</option>
                  </select>
                </div>
              </div>
              <div class="mt-4">
                <label for="repo_url">Repo URL</label>
                <div class="mt-1">
                  <input type="text" name="repo_url" placeholder="https://github.com/example/repo-name">
                </div>
              </div>
              <div class="mt-4">
                <label for="branch">Branch</label>
                <div class="mt-1">
                  <input type="text" name="branch" placeholder="main">
                </div>
              </div>
              <div class="mt-4">
                <label for="env_name">Environment Name</label>
                <div class="mt-1">
                  <input type="text" name="env_name" placeholder="development">
                </div>
                <p class="mt-2 mb-4 text-sm text-gray-500">
                  Passed to service via the <code>$ENVIRONMENT</code> variable.
                </p>
              </div>
            </div>
            <div class="flex justify-end gap-1 mt-5">
              <a href="#services">
                <button>Cancel</button>
              </a>
              <button id="add-service-button" class="main">Create</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
  return html
}

function addSiteModalView(services) {
  var html = `
    <div class="modal" name="add-site" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="modal-bg"></div>
      <div class="modal-view">
        <div class="modal-frame">
          <div class="modal-body">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
              <h3 class="modal-title" id="modal-title">New Site</h3>
              <div class="mt-4">
                <label for="site_id">Site Identifier</label>
                <div class="mt-1">
                  <input type="text" name="site_id" placeholder="example-site">
                </div>
                <p class="mt-2 mb-4 text-sm text-gray-500">
                  Site identifiers are used are used internal as a unique identifier.
                  <b>Allowed characters</b>: letters, numbers and dashes.
                </p>
              </div>
              <div class="mt-4">
                <label for="service_id">Service</label>
                <div class="mt-1">
                  <select name="service_id">
                    <option value="" disabled selected>Select a service...</option>
  `
  for (var index in services) {
    var service_id = services[index]['service_id']
    html += `
                    <option value="${service_id}">${service_id}</option>
    `
  }
  html += `
                  </select>
                </div>
                <p class="mt-2 mb-4 text-sm text-gray-500">
                  To add a service, go to the <a href="#services">services</a> page click <b>Add Service</b>.
                </p>
              </div>
            </div>
            <div class="flex justify-end gap-1 mt-5">
              <a href="#sites">
                <button>Cancel</button>
              </a>
              <button id="add-site-button" class="main">Create</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
  return html
}

function createDeploysView(deploys) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        All Deploys (${deploys.length})
      </h2>
    </div>
    <table class="table-auto">
      <thead>
        <tr>
          <th scope="col"><span class="text-gray-dark">Deploy ID</span></th>
          <th scope="col"><span class="text-gray-dark">Service ID</span></th>
          <th scope="col"><span class="text-gray-dark">Commit SHA</span></th>
          <th scope="col"><span class="text-gray-dark">Status</span></th>
          <th scope="col"><span class="text-gray-dark">Sites</span></th>
          <th scope="col"><span class="text-gray-dark">Created</span></th>
          <th scope="col"><span class="text-gray-dark">Action</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (var index in deploys) {
    var deploy = deploys[index]
    // Params
    var deploy_id = deploy['deploy_id']
    var service_id = deploy['service_id']
    var commit_sha = deploy['commit_sha'].slice(0, 6)
    var status = deploy['status']
    var created = deploy['created']
    // Sites
    var sites = {}
    for (const [index, site] of Object.entries(deploy['sites'])) {
      sites[site['site_id']] = {
        'status': site['status'],
      }
    }
    // Row
    html += `
        <tr>
          <td>${LBUI.format.value(deploy_id)}</td>
          <td><a href="#service?id=${service_id}">${LBUI.format.badge('main', service_id)}</a></td>
          <td>${LBUI.format.text.gray(commit_sha)}</td>
          <td>${LBUI.format.status(status)}</td>
          <td>${LBUI.format.value(sites)}</td>
          <td>${LBUI.format.datetime(created)}</td>
          <td><a href="#deploy?id=${deploy_id}"><button class="main">View</button></a></td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
  `
  // Result
  return html
}

function createDeployServicePanel(deploy) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        Build Service
      </h2>
      <span class="right">
        Overall: ${LBUI.format.status(deploy['status'])}
      </span>
    </div>
    <table class="table-auto">
      <thead>
        <tr>
          <th scope="col"><span class="text-gray-dark">Container ID</span></th>
          <th scope="col"><span class="text-gray-dark">Name</span></th>
          <th scope="col"><span class="text-gray-dark">Metadata</span></th>
          <th scope="col"><span class="text-gray-dark">Status</span></th>
          <th scope="col"><span class="text-gray-dark">Started</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (const [index, action] of Object.entries(deploy['actions']['pending'])) {
    var container_id = action['container_id']
    var text = action['text']
    var metadata = action['metadata']
    var status = action['status']
    var created = action['created']
    html += `
        <tr>
          <td>${LBUI.format.badge('gray', container_id)}</td>
          <td>${LBUI.format.text.medium(text)}</td>
          <td>${LBUI.format.value(metadata)}</td>
          <td>${LBUI.format.status(status)}</td>
          <td>${LBUI.format.datetime(created)}</td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
    <div class="bar mt-8">
      <h2 class="left">
        Deploy Service
      </h2>
    </div>
    <table class="table-auto">
      <thead>
        <tr>
          <th scope="col"><span class="text-gray-dark">Container ID</span></th>
          <th scope="col"><span class="text-gray-dark">Name</span></th>
          <th scope="col"><span class="text-gray-dark">Metadata</span></th>
          <th scope="col"><span class="text-gray-dark">Status</span></th>
          <th scope="col"><span class="text-gray-dark">Started</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (const [index, action] of Object.entries(deploy['actions']['complete'])) {
    var container_id = action['container_id']
    var text = action['text']
    var metadata = action['metadata']
    var status = action['status']
    var created = action['created']
    html += `
        <tr>
          <td>${LBUI.format.badge('gray', container_id)}</td>
          <td>${LBUI.format.value(text)}</td>
          <td>${LBUI.format.value(metadata)}</td>
          <td>${LBUI.format.status(status)}</td>
          <td>${LBUI.format.datetime(created)}</td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
  `
  // Result
  return html
}

function createSitesView(sites) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        All Sites (${sites.length})
      </h2>
      <div class="right">
        <a href="#sites?modal=add-site">
          <button class="main-lg">New Site</button>
        </a>
      </div>
    </div>
    <table class="table-auto">
      <thead>
        <tr>
          <th scope="col"><span class="text-gray-dark">Site ID</span></th>
          <th scope="col"><span class="text-gray-dark">Service ID</span></th>
          <th scope="col"><span class="text-gray-dark">Primary URL</span></th>
          <th scope="col"><span class="text-gray-dark">Action</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (var index in sites) {
    var site = sites[index]
    // Params
    var site_id = site['site_id']
    var service_id = site['service_id']
    // URLs
    var hostname = (site['hostnames'].length > 0) ? site['hostnames'][0] : false
    var url = (hostname) ? LBUtil.url.format(hostname['name'], hostname['ssl_cert']) : false
    // Row
    html += `
        <tr>
          <td><a href="#site?id=${site_id}">${LBUI.format.badge('dark', site_id)}</a></td>
          <td><a href="#service?id=${service_id}">${LBUI.format.badge('main', service_id)}</a></td>
          <td>${LBUI.format.link(url)}</td>
          <td><a href="#site?id=${site_id}"><button class="main">View</button></a></td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
  `
  // Result
  return html
}

function createSiteHostnamesPanel(site_id, hostnames) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        All Hostnames
      </h2>
    </div>
    <table class="col-5 mt-4">
      <thead>
        <tr>
          <th scope="col"><span>Hostname</span></th>
          <th scope="col"><span>Type</span></th>
          <th scope="col"><span>SSL Certificate</span></th>
          <th scope="col"><span>Action</span></th>
          <th scope="col"><span>Manage</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (var index in hostnames) {
    // Params
    var item = hostnames[index]
    var name = item['name']
    var primary = (index == 0)
    var ssl_cert = item['ssl_cert']
    var ssl_expires = item['ssl_expires']
    // URL
    var url = LBUtil.url.format(name, ssl_cert)
    // Construct: <tr>
    html += `
        <tr>
          <td>${LBUI.format.link(url, name)}</td>
          <td>${primary ? LBUI.format.badge('primary', 'Primary') : LBUI.format.text.light('Alternate')}</td>
    `
    if (ssl_cert) {
      html += `
          <td>${LBUI.format.badge('primary', 'Valid')} Expires: ${LBUI.format.date(ssl_expires)}</td>
      `
    } else {
      html += `
          <td>${LBUI.format.value(false)}</td>
      `
    }
    if (!primary) {
      html += `
          <td>
            <button data-hostname="${name}" class="primary primary-hostname-button">
              Make Primary
            </button>
          </td>
      `
    } else {
      html += `
          <td>${LBUI.format.value(false)}</td>
      `
    }
    if (name != window.location.hostname) {
      html += `
          <td>
            <button data-hostname="${name}" class="destructive remove-hostname-button">
              Remove Hostname
            </button>
          </td>
      `
    } else {
      html += `
          <td>${LBUI.format.value(false)}</td>
      `
    }
    html += `
        </tr>
    `
  }
  html += `
        <tr>
          <td><input id="add-hostname-input" type="text" placeholder="New hostname"></td>
          <td><button class="constructive text-bold" id="add-hostname-button">+ Add Hostname</button></td>
          <td></td>
          <td></td>
          <td></td>
        </tr>
      </tbody>
    </table>
  `
  // Result
  return html
}

function createSiteNotesPanel(site_id, notes) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        All Notes
      </h2>
    </div>
    <table class="mt-4">
      <thead>
        <tr>
          <th scope="col"><span>User ID</span></th>
          <th scope="col"><span>Name</span></th>
          <th scope="col"><span>Text</span></th>
          <th scope="col"><span>Added</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (var index in notes) {
    var note = notes[index]
    html += `
        <tr class="top">
          <td>${LBUI.format.text.medium(note['user_id'])}</td>
          <td>${LBUI.format.text.medium(note['first_name'])} ${LBUI.format.text.medium(note['last_name'])}</td>
          <td class="wide">${LBUI.format.text.gray(note['text'])}</td>
          <td>${LBUI.format.datetime(note['timestamp'])}</td>
        </tr>
    `
  }
  html += `
        <tr>
          <td>${LBUI.format.text.medium(auth['user_id'])}</td>
          <td>${LBUI.format.text.medium(auth['first_name'])} ${LBUI.format.text.medium(auth['last_name'])}</td>
          <td class="wide"><textarea id="add-note-input" placeholder="Enter text here..."></textarea>
          <td><button class="constructive text-bold" id="add-note-button">+ Add Note</button></td>
        </tr>
      </tbody>
    </table>
  `
  // Results
  return html
}

function createSiteResourcesPanel(site_id, deployment) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        Current Resources
      </h2>
    </div>
    <table class="mt-4">
      <thead>
        <tr>
          <th scope="col"><span>Name</span></th>
          <th scope="col"><span>Type</span></th>
          <th scope="col"><span>Param</span></th>
          <th scope="col"><span>Value</span></th>
          <th scope="col"><span>Environment Variable</span></th>
          <th scope="col"><span>Action</span></th>
        </tr>
      </thead>
      <tbody>
  `
  if (deployment !== false) {
    var resources = deployment['resources']
    for (const [name, config] of Object.entries(resources)) {
      var params = Object.keys(config['params']).map(
        i => `<b>${i}</b>`
      )
      var values = Object.values(config['params']).map(
        i => `<span class="gray">${i}</span>`
      )
      var env_vars = Object.keys(config['env_vars']).map(
        i => `<code>$${i}</code>`
      )
      html += `
          <tr class="top">
            <td>${LBUI.format.badge('main', name)}</td>
            <td>${LBUI.format.badge('dark', config['params']['type'])}</td>
            <td>${LBUI.format.value(params)}</td>
            <td>${LBUI.format.value(values)}</td>
            <td>${LBUI.format.value(env_vars)}</td>
            <td>${LBUI.format.value(false)}</td>
          </tr>
      `
    }
  }
  html += `
      </tbody>
    </table>
  `
  // Results
  return html
}

function createSiteEventsPanel(site_id, events) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        Audit Log
      </h2>
    </div>
    <table class="mt-4">
      <thead>
        <tr>
          <th scope="col"><span>Username</span></th>
          <th scope="col"><span>Name</span></th>
          <th scope="col"><span>Source</span></th>
          <th scope="col"><span>Action</span></th>
          <th scope="col"><span>Kind</span></th>
          <th scope="col"><span>Metadata</span></th>
          <th scope="col"><span>Timestamp</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (var index in events) {
    var event = events[index]
    html += `
        <tr class="top">
          <td>${LBUI.format.text.medium(event['user_id'])}</td>
          <td>${event['first_name']} ${event['last_name']}</td>
          <td>${LBUI.format.badge('dark', event['source'])}</td>
          <td>${LBUI.format.badge('gray', event['action'])}</td>
          <td>${LBUI.format.badge('primary', event['kind'])}</td>
          <td>${LBUI.format.value(event['metadata'])}</td>
          <td>${LBUI.format.datetime(event['timestamp'])}</td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
  `
  // Results
  return html
}

function createSiteManagePanel(site_id) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        Danger Zone
      </h2>
    </div>
    <div class="bg-white mt-4 shadow sm:rounded-lg border border-gray-200">
      <div class="p-6">
        <h3 class="text-lg font-medium text-gray-900">
          Delete Site
        </h3>
        <hr class="mt-1" />
        <div class="mt-4 text-sm text-gray-500">
          <p>
            Warning: Deleting a site will permanently erase all site data from both Wagtail and the management dashboard.
          </p>
        </div>
        <div class="mt-3">
          <button class="destructive" id="remove-site-button">Delete Site</button>
        </div>
      </div>
    </div>
  `
  // Results
  return html
}

function createServicesView(services) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        All Services (${services.length})
      </h2>
      <div class="right">
        <a href="#services?modal=add-service">
          <button class="main-lg">New Service</button>
        </a>
      </div>
    </div>
    <table class="table-auto border border-dark">
      <thead>
        <tr>
          <th scope="col"><span class="text-gray-dark">Service ID</span></th>
          <th scope="col"><span class="text-gray-dark">Service Name</span></th>
          <th scope="col"><span class="text-gray-dark">Repo URL</span></th>
          <th scope="col"><span class="text-gray-dark">Branch</span></th>
          <th scope="col"><span class="text-gray-dark">Environment Name</span></th>
          <th scope="col"><span class="text-gray-dark">Action</span></th>
        </tr>
      </thead>
      <tbody>
  `
  for (const [index, service] of Object.entries(services)) {
    // Params
    var service_id = service['service_id']
    var name = service['name']
    var repo_url = service['repo_url']
    var branch = service['branch']
    var env_name = service['env_name']
    // Row
    html += `
        <tr>
          <td><a href="#service?id=${service_id}">${LBUI.format.badge('main', service_id)}</a></td>
          <td>${name}</td>
          <td>${LBUI.format.link(repo_url)}</td>
          <td>${LBUI.format.badge('dark', branch)}</td>
          <td>${LBUI.format.badge('gray', env_name)}</td>
          <td><a href="#service?id=${service_id}"><button class="main">View</button></a></td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
  `
  // Result
  return html
}

function createServiceDeploymentsPanel(service_id, commits, deployments) {
  // Construct
  var html = `
    <div class="bar">
      <h2 class="left">
        Recent Commits
      </h2>
    </div>
    <table class="col-6 border border-dark">
      <thead>
        <tr>
          <th scope="col"><span class="text-gray-dark">Commit SHA</span></th>
          <th scope="col"><span class="text-gray-dark">Author</span></th>
          <th scope="col"><span class="text-gray-dark">Message</span></th>
          <th scope="col"><span class="text-gray-dark">Date</span></th>
          <th scope="col"><span class="text-gray-dark">Status</span></th>
          <th scope="col"><span class="text-gray-dark">Action</span></th>
        </tr>
      </thead>
      <tbody>
  `
  var complete = false
  for (var index in commits) {
    var commit = commits[index]
    var message = commit['message'].replaceAll('\n', '<br>')
    var status = false
    for (const [index, deploy] of Object.entries(deployments)) {
      if (commit['sha'] == deploy['commit_sha']) {
        status = deploy["status"]
        if (status == 'complete') {
          if (!complete) {
            complete = true
            status = 'live'
          }
        }
        break
      }
    }
    // Row
    html += `
        <tr>
          <td>${LBUI.format.link(commit['url'], commit['sha'])}</td>
          <td>${LBUI.format.link(commit['author']['url'], commit['author']['id'])}</td>
          <td class="wide-wrap">${message}</td>
          <td>${commit['date']}</td>
          <td>${(status) ? LBUI.format.status(status) : LBUI.format.value(false)}</td>
          <td><button data-commit-sha="${commit['sha']}" class="main deploy-service-button">Deploy</button></td>
        </tr>
    `
  }
  html += `
      </tbody>
    </table>
  `
  // Result
  return html
}

function createStatsOverviewRow(source, data) {
  // Params
  var html = ''
  var stats = data['stats']
  // Construct
  html += `
    <div class="bg-gray-500 overflow-hidden sm:rounded-lg border-dark mb-6">
      <div class="flex px-6 py-2">
        <div class="flex-grow text-lg font-semibold text-white">
          Name: ${source}
        </div>
        <div class="flex-1 text-right text-md text-white">
          ${LBUI.format.datetime(stats['timestamp'])}
        </div>
      </div>
      <div class="bg-white px-4 py-4 border-t border-gray-300">
  `
  // Sites
  if (stats !== false) {
    var sites = stats['sites']
    if (sites !== false) {
      html += '<dl class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-8 text-center">'
      for (var index in sites) {
        var site = sites[index]
        var site_id = site['site_id']
        var hostnames = site['hostnames']
        var status = []
        for (hostname in hostnames) {
          var code = hostnames[hostname]
          status.push((code == 200))
        }
        if (status.length > 0) {
          var color = (status.indexOf(false) > -1) ? 'bg-red-400' : 'bg-green-300'
        } else {
          var color = 'bg-gray-400'
        }
        html += `
          <div class="relative border border-gray-400 rounded-lg overflow-hidden">
            <div class="${color} px-2 py-2 font-medium text-sm">
              ${site_id}
            </div>
          </div>
        `
      }
      html += '</dl>'
    }
  } else {
    html += `
        <div class="px-2 text-gray-700 text-md">
          No recent stats reported.
        </div>
      `
  }
  html += '</div></div>'
  // Result
  return html
}

function createStatsTitleBar(count) {
  return `
    <div class="bar">
      <h2 class="left">
        Current Statistics &middot; <span class="text-gray-500">Containers: ${count}</span>
      </h2>
      <div class="right">
        <button id="monitor_reload" class="icon dark">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg> Reload
        </button>
      </div>
    </div>
  `
}

function createStatsDetailedRow(source, data) {
  // Params
  var html = ''
  var stats = data['stats']
  // Prepare
  data['created'] = data['created'] ? LBUI.format.datetime(data['created']) : 'N/A'
  data['started'] = data['started'] ? LBUI.format.datetime(data['started']) : 'N/A'
  data['status'] = data['status'] ? data['status'] : {'current': 'N/A', 'desired': 'N/A'}
  // Construct
  html += `
    <div class="bg-gray-50 overflow-hidden sm:rounded-lg border-dark mb-6">
      <div class="bg-gray-500 flex px-6 py-2">
        <div class="flex-grow text-lg font-semibold text-white">
          Name: ${source}
        </div>
        <div class="flex-1 text-right text-md text-white">
          ${LBUI.format.datetime(stats['timestamp'])}
        </div>
      </div>
      <div class="bg-white px-4 py-5 border-t border-gray-300">
        <dl class="grid grid-cols-1 gap-x-4 gap-y-8 lg:grid-cols-6 sm:grid-cols-2">
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Status: Current</dt>
            <dd class="mt-2 text-sm text-gray-900">
              ${data['status']['current']}
            </dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Status: Desired</dt>
            <dd class="mt-1 text-sm text-gray-900">
              ${data['status']['desired']}
            </dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Created</dt>
            <dd class="mt-1 text-sm text-gray-900">
              ${data['created']}
            </dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Started</dt>
            <dd class="mt-1 text-sm text-gray-900">
              ${data['started']}
            </dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">Cluster</dt>
            <dd class="mt-1 text-sm text-gray-900">
              ${data['cluster'] || 'None'}
            </dd>
          </div>
          <div class="sm:col-span-1">
            <dt class="text-sm font-medium text-gray-500">AZ</dt>
            <dd class="mt-1 text-sm text-gray-900">
              ${data['az'] || 'N/A'}
            </dd>
          </div>
        </dl>
      </div>
  `
  if (stats !== false) {
    var sites = stats['sites']
    for (var index in sites) {
      var site = sites[index]
      var site_id = site['site_id']
      var hostnames = site['hostnames']
      var uwsgi = site['uwsgi']
      html += `
        <div class="bg-gray-50 px-4 py-4 border-t border-gray-200">
          <div class="text-lg font-bold text-gray-900">
            ${site_id}
          </div>
          <div class="grid grid-cols-8 gap-2 mt-2">
            <div class="col-span-2">
              <table class="border border-gray-300">
                <thead>
                  <tr>
                    <th scope="col"><span class="text-gray-dark">Hostname</span></th>
                    <th scope="col"><span class="text-gray-dark">Status</span></th>
                  </tr>
                </thead>
                <tbody>
      `
      for (var hostname in hostnames) {
        var code = hostnames[hostname]
        var color = (code == 200) ? 'success' : 'error'
        var health = (code == 200) ? 'OK' : 'Error'
        html += `
                  <tr>
                    <td>${hostname}</td>
                    <td>${LBUI.format.badge(color, `${code}: ${health}`)}</td>
                  </tr>
        `
      }
      html += `
                </tbody>
              </table>
            </div>
            <div class="col-span-6">
              <table class="col-8 border border-gray-300">
                <thead>
                  <tr>
                    <th scope="col"><span class="text-gray-dark">Vassal</span></th>
                    <th scope="col"><span class="text-gray-dark">Worker</span></th>
                    <th scope="col"><span class="text-gray-dark">Accepting</span></th>
                    <th scope="col"><span class="text-gray-dark">Exceptions</span></th>
                    <th scope="col"><span class="text-gray-dark">Requests</span></th>
                    <th scope="col"><span class="text-gray-dark">Respawns</span></th>
                    <th scope="col"><span class="text-gray-dark">Status</span></th>
                    <th scope="col"><span class="text-gray-dark">Threads</span></th>
                  </tr>
                </thead>
                <tbody>
      `
      for (var vassal in uwsgi) {
        var workers = uwsgi[vassal]
        for (var worker in workers) {
          var item = workers[worker]
          var accepting = {
            'color': (item['accepting'] == 1) ? 'success' : 'error',
            'value': (item['accepting'] == 1) ? 'True' : 'False'
          }
          html += `
                  <tr>
                    <td>${LBUI.format.badge('main', vassal)}</td>
                    <td>${LBUI.format.badge('dark', '#' + item['id'])}</td>
                    <td>${LBUI.format.badge(accepting['color'], accepting['value'])}
                    <td>${item['exceptions']}</td>
                    <td>${item['requests']}</td>
                    <td>${item['harakiri_count']}</td>
                    <td>${item['status']}</td>
                    <td>${item['threads']['busy']}/${item['threads']['count']} busy</td>
                  </tr>
          `
        }
      }
      html += `
                </tbody>
              </table>
            </div>
          </div>
        </div>
    `
    }
  } else {
    html += `
      <div class="bg-gray-100 text-gray-700 px-6 py-2 text-md">
        No recent stats reported.
      </div>
    `
  }
  html += '</div>'
  // Result
  return html
}
