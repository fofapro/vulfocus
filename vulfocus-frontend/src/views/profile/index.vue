<template>
  <div class="app-container">
    <div v-if="user">
      <el-row :gutter="20">

        <el-col :span="6" :xs="24">
          <user-card :user="user" />
        </el-col>

        <el-col :span="18" :xs="24">
          <el-card>
            <el-tabs v-model="activeTab">
              <el-tab-pane label="Timeline" name="timeline">
                <timeline />
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>

      </el-row>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import UserCard from './components/UserCard'
import Timeline from './components/Timeline'

export default {
  name: 'Profile',
  components: { UserCard, Timeline },
  data() {
    return {
      user: {},
      activeTab: 'timeline'
    }
  },
  computed: {
    ...mapGetters([
      'name',
      'avatar',
      'roles',
      'rank'
    ])
  },
  created() {
    this.getUser()
  },
  methods: {
    getUser() {
      this.user = {
        name: this.name,
        // role: this.roles.join(' | '),
        email: 'admin@test.com',
        avatar: this.avatar,
        rank:this.rank,
      }
    }
  }
}
</script>
