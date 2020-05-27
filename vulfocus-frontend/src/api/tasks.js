import request from '@/utils/request'

export function getTask(taskId) {
  return request({
    url: '/tasks/'+taskId+'/get/',
    method: 'get'
  })
}

export function batchTask(data) {
  return request({
    url: '/tasks/batch/batch/',
    method: 'post',
    data
  })
}

export function progressTask(taskId) {
  return request({
    url: '/tasks/'+taskId+'/progress/',
    method: 'get'
  })
}
