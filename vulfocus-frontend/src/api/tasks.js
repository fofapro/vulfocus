import request from '@/utils/request'

export function getTask(task_id) {
  return request({
    url: '/tasks/'+task_id+'/get/',
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
