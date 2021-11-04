const getters = {
  sidebar: state => state.app.sidebar,
  device: state => state.app.device,
  token: state => state.user.token,
  avatar: state => state.user.avatar,
  rank: state => state.user.rank,
  name: state => state.user.name,
  roles: state => state.user.roles,
  email: state => state.user.email,
  greenhand: state => state.user.greenhand,
  permission_routes: state => state.permission.routes,
  licence: state => state.user.licence,
}
export default getters
