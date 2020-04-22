<template>
  <div class="block">
    <el-timeline>
      <el-timeline-item v-for="(item,index) of timeline" :key="index" :timestamp="item.create_date" placement="top">
        <el-card>
          <h4>启动 {{ item.name }}</h4>
          <div v-if="item.is_check_date">
          <p>通过时间{{ item.is_check_date }}</p>
          <el-button  type="success" icon="el-icon-check" circle>
          </el-button>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
  </div>
</template>

<script>
import { ContainerHisory } from '@/api/docker'
export default {
  data() {
    return {
      timeline: ""
    }

  },
  created() {
    ContainerHisory().then(response => {
      this.timeline = response.data
    })
  },

}
</script>
