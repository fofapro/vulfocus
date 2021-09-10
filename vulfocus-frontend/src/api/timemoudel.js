import request from '@/utils/request'

const baseUrl = "/time/"

/**
 * 创建时间模式
 * 时间模式信息
 */
export function start(data) {
  return request({
    url: "/time/",
    method: 'post',
    data
  })
}

export function stoptimetemp() {
  return request({
    url: "/time/",
    method: 'delete'
  })
}

export function gettimetemp() {
  return request({
    url: "/time/",
    method: 'get'
  })
}

export function timetempadd(data) {
  return request({
    url: "/timetemp/",
    method: 'post',
    data
  })
}

export function timetemplist(flag) {

  let paramFlag = ""
  if(flag === true){
    paramFlag = "flag"
  }
  if(flag === "temp"){
    paramFlag = "temp"
  }
  let url = "/timetemp/?query="+"&flag="+paramFlag
  return request({
    url: url,
    method: 'get',
  })
}

export function timetempdelete(id) {
  return request({
    url: "/timetemp/" + id + "/",
    method: 'delete',
    data:{"id":id}
  })
}

export function userranklist(page) {
  if(page === undefined || page === null){
    page = 1
  }
  return request({
    url: '/rank/user/?page='+ page,
    method: 'get'
  })
}

/**
 * 获取计时模式信息
 * @param tempId
 * @returns
 */
export function sceneGetTemp(temp_id){
  return request({
    url: '/time/'+temp_id+'/get/',
    method: 'get'
  })
}

export function timeranklist(value,page) {
  if(page === undefined || page === null){
    page = 1
  }
  return request({
    url: '/timerank/?value=' + value + '&page='+ page,
    method: 'get'
  })
}
const publicMethod = {

  getTimestamp(time) { //把时间日期转成时间戳
   return (new Date(time)).getTime() / 1000
  }

}
export {
  publicMethod
}
