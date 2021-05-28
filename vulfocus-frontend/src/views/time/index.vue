<template>
  <div class="app-container">
    <div>
      <div slot="page1">
        <el-carousel :interval="4000" type="card" height="300px" :autoplay="false" style="padding-top: 100px" align="center">
          <el-carousel-item  v-for="item in list">
            <h3><el-button plain @click="opendialog(item)">{{item.time_range}}"分钟挑战赛"
            </el-button></h3>
            <h2>描述:{{item.time_desc}}</h2>
            <h2 v-if="item.flag_status"> 挑战赛正在进行
            </h2>
            <el-button style="float: right" v-if="item.flag_status" @click="stop()">关闭</el-button>
          </el-carousel-item>
        </el-carousel>
      </div>
    </div>
  </div>
</template>

<script>
  import { GoodWizard } from 'vue-good-wizard'
  import  CountDown from 'vue2-countdown'
  import { start,timetemplist,timetempadd,stoptimetemp,gettimetemp } from '@/api/timemoudel'

export default {
  data() {
    return {
      list: [],
      allList: [],
      currentDate: new Date(),
      Donelabs:"开始",
      centerDialogVisible: false,
      item:"",
      visibleLine: "none",
      startTime:"",
      endTime:""
    }
  },
  components: {
    'vue-good-wizard': GoodWizard,
    CountDown
  },
  created(){
    this.templist()
    this.timelist()
  },
  mounted(){
  },
  methods: {
    templist(){
        timetemplist().then(response =>{
          let data = response.data.results
          this.list = data
          })
      },
    timelist(){
      gettimetemp().then(response =>{
        let data = response.data.results
        this.allList = data
      })
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
          message: '已取挑战'
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
    nextClicked(currentPage) {
      if(currentPage===2)
      {
        this.open2()
      }
      return true; //return false if you want to prevent moving to next page
    },
    backClicked(currentPage) {
      return true; //return false if you want to prevent moving to previous page
    }
  },
  watch:{
  }

}
</script>

<style scoped>
  .el-carousel__item h3 {
    color: #00a6ac;
    font-size: 14px;
    opacity: 0.75;
    line-height: 140px;
    margin: 0;
  }
  .el-carousel__item h {
    color: #00a6ac;
    font-size: 14px;
    opacity: 0.75;
    line-height: 140px;
    margin: 0;
  }

  .el-carousel__item:nth-child(2n) {
    background-color: #90d7ec;
  }

  .el-carousel__item:nth-child(2n+1) {
    background-color: #009ad6;
  }

  .el-button(){
    position:absolute;
    right:5px;
    bottom:5px;
  }
</style>

