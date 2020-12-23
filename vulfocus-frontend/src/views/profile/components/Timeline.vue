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
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="handleQuery"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
import { ContainerHisory } from '@/api/docker'
export default {
  data() {
    return {
      timeline: [],
      page: {
        size: 20,
        total: 0,
      }
    }

  },
  methods:{
    handleQuery(page){
      ContainerHisory(page).then(response => {
        // 相应数据
        this.timeline = response.data.results
        // 总数
        this.page.total = response.data.count
      })
    },
  },
  created() {
    this.handleQuery(1)
  },

}
</script>
