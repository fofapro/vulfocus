<template>
  <div class="app-container">
    <el-select v-model="value" placeholder="请选择排行榜" @change="StateChange">
      <el-option  :value="'--------'">--------</el-option>
      <el-option v-for="item in options" :key="item.time_range" :label="item.time_range" :value="item.time_range">{{item.time_range}}分钟挑战赛</el-option>
    </el-select>
    <el-table :data="tableData" border stripe style="width: 100%">
      <el-table-column type="index" width="50"></el-table-column>
      <el-table-column prop="name" label="用户名"></el-table-column>
      <el-table-column prop="rank" label="Rank"></el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="initUserList"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>

</template>

<script>
  import { userranklist,timeranklist,timetemplist } from '@/api/timemoudel'
  export default {
    inject: ['reload'],
    name: 'user',
    data(){
      return {
        page:{
          total: 0,
          size: 20,
        },
        options: [],
        tableData: [],
        status:"all",
        value:"",
        selectState:"",
        test:[]
      }
    },
    created(){
      this.initUserList(1)
      this.templist()
    },
    methods:{
      StateChange(value){
        this.value = value
        if (this.value==='--------'){
            this.reload()
        }else {
          timeranklist(this.value).then(response => {
            let data = response.data.results
            this.tableData = data
          })
        }
      },
      templist(){
        timetemplist(true).then(response =>{
          let data = response.data.results
          this.options = data
          })
      },
      initUserList(page){
        userranklist(page).then(response => {
          let data = response.data.results
          this.tableData = data
          this.page.total = response.data.count
        })
      },
    }
  }
</script>

<style scoped>

</style>
