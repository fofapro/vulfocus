<template>
<div class="app-container">
  <div class="filter-container">
    <el-input v-model="search" style="width: 230px;" size="medium"></el-input>
    <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleQuery">
      查询
    </el-button>
    <el-row :gutter="23">
      <el-col :span="6" v-for="(item,index) in tableData" :key="index" style="padding-bottom: 18px;">
        <el-card :body-style="{ padding: '8px'}" shadow="hover">
          <div class="clearfix" style="margin-top: 5px">
            <div style="display: inline-block;height: 20px;line-height: 20px;min-height: 20px;max-height: 20px;">
              <svg-icon icon-class="bug"  style="font-size: 20px;"/>
            </div>
          </div>
          <div style="padding: 5px; margin-top: 5px;" >
            <img v-if="item.image_name !==imgpath" :src="item.image_name"  alt="" width="285px" height="300px;"/>
            <img v-else-if="item.image_name===imgpath" :src="modelimg"  alt="" width="285px" height="300px;"/>
            <div class="container-title" style="margin-top: 5px;">
              <span>{{item.layout_name}}</span>
            </div>
            <div class="bottom clearfix" style="margin-top: 10px;height: 80px;">
              <span style="color:#999;font-size: 13px;" class="hoveDesc"> {{ item.layout_desc }}</span>
            </div>
            <span>编排模式</span>
            <el-row style="margin-top: 5px;margin-bottom: 10px; float: right">
              <el-button type="primary" size="mini" @click="handleInto(item)">进入</el-button>
            </el-row>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" v-for="(titem,index) in timelist" :key="index" style="padding-bottom: 18px;">
        <el-card :body-style="{ padding: '8px'}" shadow="hover">
          <div class="clearfix" style="margin-top: 5px">
            <div style="display: inline-block;height: 20px;line-height: 20px;min-height: 20px;max-height: 20px;">
              <svg-icon icon-class="bug"  style="font-size: 20px;"/>
            </div>
          </div>
          <div style="padding: 5px; margin-top: 5px;" >
            <img v-if="titem.image_name !== imgpath" :src= "titem.image_name"  alt="" width="285px" height="300px;"/>
            <img v-else-if="titem.image_name===imgpath" :src= "modelimg"  alt="" width="285px" height="300px;"/>
            <div class="container-title" style="margin-top: 5px;">
              <span>{{titem.name}}</span>
            </div>
            <div class="bottom clearfix" style="margin-top: 10px;height: 80px;" >
              <span style="color:#999;font-size: 13px;" class="hoveDesc"> 描述:{{ titem.time_desc }}</span>
              <span style="color:#999;font-size: 13px;" class="hoveDesc"> 时间:{{ titem.time_range }}分钟</span>
              <span style="color:#999;font-size: 14px;" class="hoveDesc" v-if="titem.rank_range !== undefined && titem.rank_range > 0"> rank:{{ titem.rank_range }}</span>
              <span style="color:#999;font-size: 13px;" class="hoveDesc" v-if="countlist.length >0 && titem.temp_id === countlist[0].temp_time_id">倒计时
              <count-down v-if="countlist.length >0 && countlist[0].temp_time_id === titem.temp_id" v-on:end_callback="autostop()" :currentTime="countlist[0].start_date" :startTime="countlist[0].start_date" :endTime="countlist[0].end_date" :dayTxt="'天'" :hourTxt="'小时'" :minutesTxt="'分钟'" :secondsTxt="'秒'">
              </count-down>
              </span>
            </div>
            <span>计时模式</span>
            <el-row style="margin-top: 5px;margin-bottom: 10px; float: right" v-if="countlist.length !==0">
              <el-button type="primary" size="mini" v-if="titem.temp_id!== countlist[0].temp_time_id" @click="handleOk(titem)" >开始</el-button>
              <el-button type="primary" size="mini" v-if="titem.temp_id === countlist[0].temp_time_id" @click="stop()">关闭</el-button>
            </el-row>
            <el-row style="margin-top: 5px;margin-bottom: 10px; float: right" v-else-if="countlist.length===0">
              <el-button type="primary" size="mini" @click="opendialog(titem)" >开始</el-button>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

  </div>
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
import { layoutList } from '@/api/layout'
import CountDown from 'vue2-countdown'
import { start,timetemplist,timetempadd,stoptimetemp,gettimetemp,publicMethod } from '@/api/timemoudel'
export default {
  name: 'index',
  components: {
    CountDown
  },
  data(){
    return {
      tableData: [],
      search: "",
      page:{
        total: 0,
        size: 20,
      },
      get_time:"",
      timelist:[],
      countlist:[],
      imgpath: '/images/',
      modelimg: require("../../assets/modelbg.jpg")
      // isAdmin: false
    }
  },
  methods: {
    layoutList(page){
      this.tableData = []
      layoutList(this.search, page, "flag").then(response => {
        let rsp = response.data
        rsp.results.forEach((info,index) => {
          info.image_name = '/images/'+ info.image_name
          this.tableData.push(info)
        })
        this.page.total = rsp.count
      }).catch(err => {
        this.$message({
          type: 'error',
          message: '服务器内部错误!'
        })
      })
    },
    gettimelist(){
      gettimetemp().then(response => {
        let data = response.data.results
          this.countlist = data
          if (this.countlist.length===0){
          }else {
            this.countlist[0].end_date = publicMethod.getTimestamp(this.countlist[0].end_date)
            this.countlist[0].start_date = publicMethod.getTimestamp(this.get_time)
          }
        }
      )
    },
    handleQuery(){
      this.layoutList(1)
    },
    handleInto(item){
      this.$router.push({path: "/scene/index", query: {"layout_id": item.layout_id}})
    },
    templist(){
        timetemplist().then(response =>{
          let data = response.data
          data.results.forEach((info,index) => {
            info.image_name = '/images/'+ info.image_name
            this.timelist.push(info)
          })
          this.page.total += data.count
        })
    },
    handleOk(titem){
      if (this.countlist.length!=0){
        this.$message({
          message: '已有时间模式在运行，请先关闭',
          type: 'error'
        })
        return
      }else{
        this.opendialog(titem)
      }
    },
    opendialog(item){
      this.item = item
      if (item.flag_status===true){
        this.$message({
          type:"error",
          message:item.time_range + "分钟挑战赛已经开始"
        })
      }else{
      this.$confirm('是否开始挑战?', '提示', {
        center: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        start(item).then(response => {
          const data = response.data;
          let msgType = 'success';
          let msg = '';
          if('200'===data.code){
            msg = '计时模式开始启动！'
          }else if ('2001' === data.code){
            msg = '计时模式已经启动，请勿重新启动'
          }else{
            msgType = 'error';
            msg = '内部错误';
          }
          this.$message({
            type: msgType,
            message: msg,
          });
        })
        this.$router.push({ path: '/dashboard' })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消挑战'
        });
      });
    }},
    stop(){
      this.$confirm('是否取消挑战?', '提示', {
        center: true,
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        stoptimetemp().then(response => {
          const data = response.data;
          let msgType = 'success';
          let msg = '';
          if('2000'===data.code){
            msg = '计时模式已经关闭！'
          }else{
            msgType = 'error';
            msg = '关闭失败,内部错误';
          }
          this.$message({
            type: msgType,
            message: msg,
          });
        })
        this.$router.push({ path: '/dashboard' })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消'
        });
      });
    },
    autostop(){
      stoptimetemp().then(response => {
          const data = response.data;
          let msgType = 'success';
          let msg = '';
          if('2000'===data.code){
            msg = '计时模式已经关闭！'
          }else{
            msgType = 'error';
            msg = '关闭失败,内部错误';
          }
          this.$message({
            type: msgType,
            message: msg,
          });
        })
    }
  },
  created() {
    this.handleQuery()
    this.templist()
    this.gettimelist()
  },
  mounted: function() {
      var _this = this;
      let yy = new Date().getFullYear();
      let mm = new Date().getMonth()+1;
      let dd = new Date().getDate();
      let hh = new Date().getHours();
      let mf = new Date().getMinutes()<10 ? '0'+new Date().getMinutes() : new Date().getMinutes();
      let ss = new Date().getSeconds()<10 ? '0'+new Date().getSeconds() : new Date().getSeconds();
      _this.get_time = yy+'-'+mm+'-'+dd+' '+hh+':'+mf+':'+ss;
  }
}
</script>

<style scoped>
.hoveDesc {
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  -o-text-overflow: ellipsis;
  white-space: nowrap;
  /*word-break:normal;*/
  width:auto;
  display:block;
  word-break:keep-all;
  margin-top: 2px;
}
</style>
