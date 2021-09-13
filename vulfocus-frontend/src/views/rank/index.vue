<template>
  <div class="app-container">
    <el-select v-model="value" placeholder="请选择排行榜" @change="StateChange">
      <el-option value="总榜">总榜</el-option>
    </el-select>
    <el-table :data="tableData" border stripe style="margin-top: 20px" >
      <el-table-column type="index" label="排名" width="100px">
        <template slot-scope="scope">
          <p v-if="page.currentPageNum*page.size+scope.$index+1-page.size>=4" style="margin-left:17px">{{page.currentPageNum*page.size+scope.$index+1-page.size}}</p>
          <svg-icon icon-class="trophy1" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===1"  style="width: 50px;height: 50px"/>
          <svg-icon icon-class="trophy2" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===2"  style="width: 40px;height: 40px;margin-left:5px"/>
          <svg-icon icon-class="trophy3" v-if="page.currentPageNum*page.size+scope.$index+1-page.size===3"  style="width: 30px;height: 30px;margin-left:8px"/>
        </template>
      </el-table-column>
      <el-table-column label="用户">
        <template slot-scope="scope">
          <img :src="scope.row.image_url" style="width: 30px;height: 30px;border-radius: 50%;float: left;margin-top: 10px">
          <p style="float: left;margin-left: 5px;margin-top: 14px">{{scope.row.name}}</p>
        </template>
      </el-table-column>
      <el-table-column prop="rank" label="积分"></el-table-column>
      <el-table-column prop="pass_container_count" label="通过数量" v-if="pass_vul_show"></el-table-column>
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
          currentPageNum:1,
        },
        options: [],
        tableData: [],
        status:"all",
        value: "",
        selectState:"",
        test:[],
        pass_vul_show:true
      }
    },
    created(){
      // this.initUserList(1)
      this.getUserlist(1)
      this.templist()
    },
    methods:{
      StateChange(value){
        this.value = value
        if (this.value ==='总榜'){
            this.reload()
        }else {
          timeranklist(this.value).then(response => {
            this.tableData = response.data.results
            this.page.total = response.data.count
            this.page.currentPageNum = 1
            this.pass_vul_show=false
          })
        }
      },
      getUserlist(page){
        this.value = "总榜"
        userranklist(page).then(response => {
          this.tableData = response.data.data.results
          this.page.total = response.data.data.count
          this.page.currentPageNum = page
        })
      },
      templist(){
        timetemplist(true).then(response =>{
          this.options = response.data.results
          })
      },
      initUserList(page){
        if (this.value === '总榜'){
        userranklist(page).then(response => {
          this.tableData = response.data.data.results
          this.page.total = response.data.data.count
          this.page.currentPageNum = page
        })}else {
          timeranklist(this.value,page).then(response => {
            this.tableData = response.data.results
            this.page.total = response.data.count
            this.page.currentPageNum = page
            this.pass_vul_show=false
          })
        }
      },
    }
  }
</script>

<style scoped>

</style>
