class LBUtil {}

LBUtil.poll = class {
  static interval = false
  static reset() {
    if (LBUtil.poll.interval) {
      clearInterval(LBUtil.poll.interval)
      LBUtil.poll.interval = false
    }
  }
  static start(func, delay) {
    LBUtil.poll.reset()
    LBUtil.poll.interval = setInterval(func, delay)
  }
}

LBUtil.url = class {
  static format(hostname, ssl=true) {
    // Params
    var proto = (ssl) ? 'https' : 'http'
    var port = false
    if (window.location.port) {
      port = (ssl) ? 8443 : 8080
    }
    var url = (proto + '://' + hostname)
    // Result
    return (port) ? `${url}:${port}` : url
  }
}

class LBUI {}

LBUI.format = class {
  static badge(kind, text) {
    return `<span class="badge ${kind}">${text}</span>`
  }
  static capitalize(text) {
    return `${text[0].toUpperCase()}${text.slice(1).toLowerCase()}`
  }
  static date(seconds) {
    if (seconds !== undefined) {
      return new Date(seconds * 1000).toLocaleDateString('en-US')
    }
    return LBUI.format.text.light('N/A')
  }
  static datetime(seconds) {
    if (seconds !== undefined) {
      return new Date(seconds * 1000).toLocaleString('en-US')
    }
    return LBUI.format.text.light('N/A')
  }
  static link(url, name=false) {
    if (!url) {
      return LBUI.format.value(false)
    }
    name = (name) ? name : url
    return `<a href="${url}" target="_blank">${name}</a>`
  }
  static status(value) {
    var color = {
      'complete': 'success',
      'current': 'main',
      'failed': 'error',
      'live': 'main',
      'pending': 'dark'
    }[value]
    return LBUI.format.badge(color, LBUI.format.capitalize(value))
  }
  static value(input, level=0) {
    if (typeof(input) == 'object') {
      if (Object.keys(input).length > 0) {
        // Array or Dictionary
        var array = Array.isArray(input)
        var rows = Object.keys(input).map(function(key) {
          var item = input[key]
          item = (typeof(item) == 'boolean') ? String(item) : item
          item = LBUI.format.value(item, (level + 1))
          return (array) ? `<li>${item}</li>` : `<li><b>${key}:</b> ${item}</li>`
        })
        var classes = (level > 0) ? 'list-disc ml-8' : 'ml-0'
        return `<ul class="${classes}">${rows.join('')}</ul>`
      }
      return LBUI.format.value(false)
    }
    // Optional Value
    return (input) ? input : LBUI.format.text.light('N/A')
  }
}

LBUI.format.text = class {
  static bold(value) {
    return LBUI.format.text.span('bold', value)
  }
  static gray(value) {
    return LBUI.format.text.span('gray', value)
  }
  static light(value) {
    return LBUI.format.text.span('light', value)
  }
  static medium(value) {
    return LBUI.format.text.span('medium', value)
  }
  static span(color, value) {
    return `<span class="${color}">${value}</span>`
  }
}
