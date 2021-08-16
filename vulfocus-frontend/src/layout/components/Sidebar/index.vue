<template>
  <div :class="{'has-logo':showLogo}">
    <el-row style="height: 90%">
      <logo v-if="showLogo" :collapse="isCollapse" />
      <el-scrollbar wrap-class="scrollbar-wrapper">
        <div style="font-size: 12px;margin: 17px;">
          <img src="logo.svg" />
        </div>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :background-color="variables.menuBg"
          :text-color="variables.menuText"
          :unique-opened="false"
          :active-text-color="variables.menuActiveText"
          :collapse-transition="false"
          mode="vertical"
        >
          <sidebar-item v-for="route in permission_routes" :key="route.path" :item="route" :base-path="route.path" />
        </el-menu>
      </el-scrollbar>
    </el-row>
    <el-row style="height: 10%;margin-top: 18%;">
      <el-col>
        <div>
          <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :background-color="variables.menuBg"
          :text-color="variables.menuText"
          :unique-opened="false"
          :active-text-color="variables.menuActiveText"
          :collapse-transition="false"
          mode="vertical"
          >
            <el-menu-item class="nest-menu" >
              <div style="margin-left: 15%">
                <i class="el-icon-collection-tag" style="color: rgb(191, 203, 217);"></i>
                <span slot="title" style="color: rgb(191, 203, 217); ">  v3.2.6</span>
              </div>
            </el-menu-item>
          </el-menu>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import Logo from './Logo'
import SidebarItem from './SidebarItem'
import variables from '@/styles/variables.scss'

export default {
  components: { SidebarItem, Logo },
  computed: {
    ...mapGetters([
      'permission_routes',
      'sidebar'
    ]),
    /*
    routes() {
      console.log(this.$router.options.routes)
      return this.$router.options.routes
    },*/
    activeMenu() {
      const route = this.$route
      const { meta, path } = route
      // if set path, the sidebar will highlight the path you set
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    },
    showLogo() {
      return this.$store.state.settings.sidebarLogo
    },
    variables() {
      return variables
    },
    isCollapse() {
      return !this.sidebar.opened
    }
  }
}
</script>
