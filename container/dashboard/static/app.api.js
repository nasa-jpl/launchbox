class LBAPI {
  static get(endpoint, callback) {
    axios
      .get(endpoint)
      .then(function(response) {
        // Success
        var result = new LBAPI.result(response)
        callback(result)
      })
      .catch(function(error) {
        // Log
        console.log(error)
        // Error
        var result = new LBAPI.result(error.response)
        callback(result)
      })
      .then(function() {
        //
      })
  }
  static post(endpoint, params, callback) {
    axios
      .post(endpoint, params)
      .then(function(response) {
        // Success
        var result = new LBAPI.result(response)
        callback(result)
      })
      .catch(function(error) {
        // Log
        console.log(error)
        // Error
        var result = new LBAPI.result(error.response)
        callback(result)
      })
      .then(function() {
        //
      })
  }
  static status(callback) {
    LBAPI.get('/api/', callback)
  }
}

LBAPI.result = class {
  constructor(response) {
    this.data = response.data
    this.status = response.status
  }
  valid() {
    return ((this.status >= 200) && (this.status <= 300))
  }
}

LBAPI.auth = class {
  static state(callback) {
    LBAPI.get('/api/auth/state', callback)
  }
}

LBAPI.deploys = class {
  static get(deploy_id, callback) {
    LBAPI.get(`/api/deploys/${deploy_id}`, callback)
  }
  static list(callback) {
    LBAPI.get('/api/deploys', callback)
  }
}

LBAPI.search = class {
  static users(query, callback) {
    var endpoint = `/api/search/users/${query}`
    LBAPI.get(endpoint, callback)
  }
}

LBAPI.services = class {
  static add(service_id, name, provider_id, repo_url, branch, env_name, callback) {
    var endpoint = `/api/services/${service_id}/add`
    var params = {
      'name': name,
      'provider_id': provider_id,
      'repo_url': repo_url,
      'branch': branch,
      'env_name': env_name,
    }
    LBAPI.post(endpoint, params, callback)
  }
  static deploy(service_id, commit_sha, callback) {
    var endpoint = `/api/services/${service_id}/deploy/${commit_sha}`
    LBAPI.post(endpoint, false, callback)
  }
  static get(service_id, callback) {
    var endpoint = `/api/services/${service_id}`
    LBAPI.get(endpoint, callback)
  }
  static list(callback) {
    LBAPI.get('/api/services', callback)
  }
}

LBAPI.sites = class {
  static add(site_id, service_id, callback) {
    var endpoint = `/api/sites/${site_id}/add`
    var params = {'service_id': service_id}
    LBAPI.post(endpoint, params, callback)
  }
  static export(site_id, callback) {
    var endpoint = `/api/sites/${site_id}/content`
    LBAPI.get(endpoint, callback)
  }
  static get(site_id, callback) {
    var endpoint = `/api/sites/${site_id}`
    LBAPI.get(endpoint, callback)
  }
  static list(callback) {
    LBAPI.get('/api/sites', callback)
  }
  static remove(site_id, callback) {
    var endpoint = `/api/sites/${site_id}/remove`
    LBAPI.post(endpoint, false, callback)
  }
  static reset_db(site_id, callback) {
    var endpoint = `/api/sites/${site_id}/reset_db`
    LBAPI.post(endpoint, false, callback)
  }
  static update(site_id, attr, value, callback) {
    var endpoint = `/api/sites/${site_id}/update`
    var params = {'attr': attr, 'value': value}
    LBAPI.post(endpoint, params, callback)
  }
}

LBAPI.sites.hostnames = class {
  static add(site_id, hostname, callback) {
    var endpoint = `/api/sites/${site_id}/hostnames/add`
    var params = {'hostname': hostname}
    LBAPI.post(endpoint, params, callback)
  }
  static list(site_id, callback) {
    var endpoint = `/api/sites/${site_id}/hostnames`
    LBAPI.get(site_id, callback)
  }
  static primary(site_id, hostname, callback) {
    var endpoint = `/api/sites/${site_id}/hostnames/primary`
    var params = {'hostname': hostname}
    LBAPI.post(endpoint, params, callback)
  }
  static remove(site_id, hostname, callback) {
    var endpoint = `/api/sites/${site_id}/hostnames/remove`
    var params = {'hostname': hostname}
    LBAPI.post(endpoint, params, callback)
  }
}

LBAPI.sites.notes = class {
  static add(site_id, text, callback) {
    var endpoint = `/api/sites/${site_id}/notes/add`
    var params = {'text': text}
    LBAPI.post(endpoint, params, callback)
  }
}

LBAPI.stats = class {
  static latest(callback) {
    LBAPI.get('/api/stats/latest', callback)
  }
}
