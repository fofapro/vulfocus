import { login, logout, getInfo,register } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { resetRouter } from '@/router'
import {  Message } from 'element-ui'

const state = {
  token: getToken(),
  name: '',
  avatar: '',
  rank:'',
  email:'',
  roles: [],
}

const mutations = {
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_RANK: (state, rank) => {
    state.rank = rank
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  }
}

const actions = {
  // user login
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password }).then(response => {
        const { data } = response
        commit('SET_TOKEN', data.token)
        setToken(data.token)
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },
  register({ commit }, userInfo) {
    const { name,pass,checkPass,email} = userInfo
    return new Promise((resolve, reject) => {
      register({ username: name.trim(), password: pass ,email:email}).then(response => {
        resolve(response)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // get user info
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo(state.token).then(response => {
        const { data } = response
        if (!data) {
          reject('Verification failed, please Login again.')
        }
        const { name, avatar,rank, roles } = data
        commit('SET_NAME', name)
        commit('SET_AVATAR', avatar)
        commit('SET_RANK', rank)
        commit("SET_ROLES", roles)
        resolve(data)
      }).catch(error => {
        reject(error)
      })
    })
  },

  // user logout
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      logout(state.token).then(() => {
        commit('SET_TOKEN', '')
        removeToken()
        commit('SET_ROLES', [])
        resetRouter()
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // remove token
  resetToken({ commit }) {
    return new Promise(resolve => {
      commit('SET_TOKEN', '')
      commit('SET_ROLES', [])
      removeToken()
      console.log("删除COOKIE")
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}

