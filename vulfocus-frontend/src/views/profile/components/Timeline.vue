<template>
  <div class="block">
    <el-timeline v-if="timemodel===false" >
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
    <el-timeline v-else-if="timemodel===true" >
      <el-timeline-item placement="top">
          <el-card>
            <h4>正在进行计时挑战赛</h4>
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
import { gettimetemp } from '@/api/timemoudel'
export default {
  data() {
    return {
      timeline: [],
      page: {
        size: 20,
        total: 0,
      },
      timemodel:false
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
    gettimelist(){
      gettimetemp().then(response => {
        let data = response.data.results
          if (data.length===0){
          }else {
            this.timemodel = true
          }
        }
      )
    },
  },
  created() {
    this.handleQuery(1)
    this.gettimelist()
  },

}
</script>
