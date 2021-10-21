import request from '@/utils/request'

/**
 * 获取信息
 * @param layoutId
 * @returns
 */
export function sceneGet(layoutId){
  return request({
    url: '/layout/'+layoutId+'/get/',
    method: 'get'
  })
}

/**
 * 启动模式
 * @param layoutId 环境ID
 * @returns
 */
export function sceneStart(layoutId){
  return request({
    url: '/layout/'+layoutId+'/start/',
    method: 'get'
  })
}

/**
 * 关闭模式
 * @param layoutId
 * @returns {AxiosPromise}
 */
export function sceneStop(layoutId){
  return request({
    url: '/layout/'+layoutId+'/stop/',
    method: 'get'
  })
}

/**
 * 提交Flag
 * @param layoutId layoutId
 * @param flag flag
 * @returns
 */
export function sceneFlag(layoutId, flag){
  return request({
    url: '/layout/'+layoutId+'/flag/?flag='+flag,
    method: 'get'
  })
}

/**
 * 排名
 * @param layoutId
 * @returns
 */
export function sceneRank(layoutId,page){
  if (page === undefined || page === null || page < 1){
    page = 1
  }
  return request({
    url: '/layout/'+layoutId+'/rank/?page='+page,
    method: 'get'
  })
}

/**
 * 场景数据
 * @param page scene_tag
 * @returns
 */
export function getSceneData(query,page,tag,backstage){
  if(query === undefined || query == null){
    query = ""
  }
  if (tag === undefined || tag === null){
    tag = "all"
  }
  if (page === undefined || page === null || page < 1){
    page = 1
  }
  if (backstage === undefined || backstage === null){
    backstage = ""
  }
  return request({
    url: '/get/scenedata/?tag='+tag+'&page='+page+'&query=' + query + '&backstage='+backstage,
    method: 'get'
  })
}


export function thumbup(id){
  return request({
    url:'/thumbUp',
    method: 'post',
    data: {"scene_id":id}
  })
}
