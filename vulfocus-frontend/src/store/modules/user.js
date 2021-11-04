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
  greenhand: false,
  licence:'',
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
  },
  SET_EMAIL: (state, email) => {
    state.email = email
  },
  SET_GREENHAND: (state, greenhand) => {
    state.greenhand = greenhand
  },
  SET_LICENCE: (state, licence) => {
    state.licence = licence
  },
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
    const { name,pass,checkpass,email,captcha_code,hashkey} = userInfo
    return new Promise((resolve, reject) => {
      register({ username: name.trim(), password: pass ,email:email, checkpass:checkpass, captcha_code:captcha_code, hashkey:hashkey }).then(response => {
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
        const { name, avatar,rank, roles, email, greenhand, licence } = data
        commit('SET_NAME', name)
        commit('SET_AVATAR', avatar)
        commit('SET_RANK', rank)
        commit("SET_ROLES", roles)
        commit("SET_EMAIL", email)
        commit("SET_GREENHAND", greenhand)
        commit("SET_LICENCE", licence)
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

