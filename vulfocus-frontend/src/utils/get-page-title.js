import defaultSettings from '@/settings'
import request from '@/utils/request'

const title = defaultSettings.title || 'Vue Admin Template'
let t = ""

export default function getPageTitle(pageTitle) {
  if (pageTitle) {
    getUrlName().then(res=>{
      t = res
    })
    if (t.data){
      return `${pageTitle} - ${t.data}`
    }else {
      return `${pageTitle} - ${title}`
    }

  }else {
    getUrlName().then(res=>{
      t = res
      document.title = t.data || 'vulfocus'
    })
    return `${title}`
  }
}
function getUrlName() {
  return request({
    url: "get/urlname",
    method: 'get'
  })
}

