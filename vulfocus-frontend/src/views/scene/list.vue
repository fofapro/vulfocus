<template>
<div class="app-container">
  <el-input v-model="search" class="sceneSearch" size="medium" placeholder="请输入关键字进行搜索" @keyup.enter.native="handleQuery">
    <i slot="prefix" class="el-input__icon el-icon-search"></i>
  </el-input>
  <el-tabs v-model="activeName" style="margin-top: 10px" @tab-click="currentTabs">
    <el-tab-pane label="全部" name="all">
      <div class="filter-container">
        <el-row :gutter="23">
          <el-col :span="6" v-for="(item,index) in sceneTableData" :key="index" style="padding-bottom: 18px;">
            <el-card :body-style="{ padding: '0px'}">
              <div style="position: relative">
                <div class="main" style=" position: absolute">
                  <span class="word" v-if="item.type === 'layoutScene'">普通场景</span>
                  <span class="word" v-else-if="item.type === 'timeScene'">盲盒模式</span>
                </div>
                <img v-if="item.image_name !==imgpath" @click="handleInto(item)" :src="item.image_name"  alt="" width="100%" height="300px"/>
                <img v-else-if="item.image_name===imgpath" @click="handleInto(item)" :src="modelimg"  alt="" width="100%" height="300px" />
                <div class="container-title" style="margin-top: 5px;">
                  <span style="color:#303133;margin-left: 5px;font-size: 14px;">{{item.name}}</span>
                </div>
                <div class="bottom clearfix" style="margin-top: 10px;height: 60px;">
                  <span style="color:#999;font-size: 14px;margin-left: 5px;" class="hoveDesc"> {{ item.desc }}</span>
                </div>
                <div class="bottom-img" style="margin-top: 5px;width: 100%;height: 20px;margin-bottom: 10px">
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-if="item.have_fav === true"><svg-icon icon-class="fav_active" style="margin-right: 10px" @click="thumbup(item)"/>{{item.fav_num}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-else-if="item.have_fav === false"><svg-icon icon-class="fav_not_active" style="margin-right: 10px" @click="thumbup(item)"/>{{item.fav_num}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px"><svg-icon icon-class="has_read" style="margin-right: 10px"/>{{item.total_view}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-if="item.type === 'layoutScene'"><svg-icon icon-class="download" style="margin-right: 10px"/>{{item.download_num}}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-tab-pane>
    <el-tab-pane label="热门" name="hot">
      <div class="filter-container">
        <el-row :gutter="23">
          <el-col :span="6" v-for="(item,index) in sceneTableData" :key="index" style="padding-bottom: 18px;">
            <el-card :body-style="{ padding: '0px'}">
              <div style="position: relative">
                <div class="main" style=" position: absolute">
                  <span class="word" v-if="item.type === 'layoutScene'">普通场景</span>
                  <span class="word" v-else-if="item.type === 'timeScene'">盲盒模式</span>
                </div>
                <img v-if="item.image_name !==imgpath" @click="handleInto(item)" :src="item.image_name"  alt="" width="100%" height="300px"/>
                <img v-else-if="item.image_name===imgpath" @click="handleInto(item)" :src="modelimg"  alt="" width="100%" height="300px" />
                <div class="container-title" style="margin-top: 5px;">
                  <span style="color:#303133;margin-left: 5px;font-size: 14px;">{{item.name}}</span>
                </div>
                <div class="bottom clearfix" style="margin-top: 10px;height: 60px;">
                  <span style="color:#999;font-size: 14px;margin-left: 5px;" class="hoveDesc"> {{ item.desc }}</span>
                </div>
                <div class="bottom-img" style="margin-top: 5px;width: 100%;height: 20px;margin-bottom: 10px">
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-if="item.have_fav === true"><svg-icon icon-class="fav_active" style="margin-right: 10px" @click="thumbup(item)"/>{{item.fav_num}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-else-if="item.have_fav === false"><svg-icon icon-class="fav_not_active" style="margin-right: 10px" @click="thumbup(item)"/>{{item.fav_num}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px"><svg-icon icon-class="has_read" style="margin-right: 10px"/>{{item.total_view}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-if="item.type === 'layoutScene'"><svg-icon icon-class="download" style="margin-right: 10px"/>{{item.download_num}}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-tab-pane>
    <el-tab-pane label="计时场景" name="time">
      <div class="filter-container">
        <el-row :gutter="23">
          <el-col :span="6" v-for="(item,index) in sceneTableData" :key="index" style="padding-bottom: 18px;">
            <el-card :body-style="{ padding: '0px'}">
              <div style="position: relative">
                <div class="main" style=" position: absolute">
                  <span class="word" v-if="item.type === 'layoutScene'">普通场景</span>
                  <span class="word" v-else-if="item.type === 'timeScene'">盲盒模式</span>
                </div>
                <img v-if="item.image_name !==imgpath" @click="handleInto(item)" :src="item.image_name"  alt="" width="100%" height="300px"/>
                <img v-else-if="item.image_name===imgpath" @click="handleInto(item)" :src="modelimg"  alt="" width="100%" height="300px" />
                <div class="container-title" style="margin-top: 5px;">
                  <span style="color:#303133;margin-left: 5px;font-size: 14px;">{{item.name}}</span>
                </div>
                <div class="bottom clearfix" style="margin-top: 10px;height: 60px;">
                  <span style="color:#999;font-size: 14px;margin-left: 5px;" class="hoveDesc"> {{ item.desc }}</span>
                </div>
                <div class="bottom-img" style="margin-top: 5px;width: 100%;height: 20px;margin-bottom: 10px">
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-if="item.have_fav === true"><svg-icon icon-class="fav_active" style="margin-right: 10px" @click="thumbup(item)"/>{{item.fav_num}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-else-if="item.have_fav === false"><svg-icon icon-class="fav_not_active" style="margin-right: 10px" @click="thumbup(item)"/>{{item.fav_num}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px"><svg-icon icon-class="has_read" style="margin-right: 10px"/>{{item.total_view}}</span>
                  <span style="color: #999;font-size: 14px;margin-left: 10px" v-if="item.type === 'layoutScene'"><svg-icon icon-class="download" style="margin-right: 10px"/>{{item.download_num}}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-tab-pane>
  </el-tabs>
  <div style="margin-top: 20px">
    <el-pagination
      :page-size="page.size"
      @current-change="getScene"
      layout="total, prev, pager, next, jumper"
      :total="page.total">
    </el-pagination>
  </div>
</div>
</template>

<script>
import { layoutList } from '@/api/layout'
import CountDown from 'vue2-countdown'
import { getSceneData,thumbup } from '@/api/scene'
import { start,timetemplist,timetempadd,stoptimetemp,gettimetemp,publicMethod } from '@/api/timemoudel'
export default {
  name: 'index',
  inject: ['reload'],
  components: {
    CountDown
  },
  data(){
    return {
      tableData: [],
      sceneTableData:[],
      sceneDict:{},
      search: "",
      page:{
        total: 0,
        size: 20,
      },
      get_time:"",
      timelist:[],
      countlist:[],
      imgpath: '/images/',
      modelimg: require("../../assets/modelbg.jpg"),
      // isAdmin: false
      activeName:'all',
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
      this.getScene(1)
    },
    handleInto(item){
      if (item.type === 'layoutScene'){
        this.$router.push({path: "/scene/index", query: {"layout_id": item.id}})
      }
      if (item.type === 'timeScene'){
        this.$router.push({path:"/timelist/index", query: {"temp_id": item.id}})
      }

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
      if (this.countlist.length!==0){
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
    },
    currentTabs(tab, event){
      this.activeName = tab.name
      this.getScene(1,this.activeName)
    },
    getScene(page){
      getSceneData(this.search,page,this.activeName).then(response=>{
        this.sceneDict = {}
        this.sceneTableData = []
        if (response.data.code === 200){
          response.data.result.forEach((info,index) => {
            info.image_name = '/images/'+ info.image_name
            this.sceneTableData.push(info)
            this.sceneDict[info.id] = info
          })
          this.page.total = response.data.count
        }else {
          this.$message({
          type: 'error',
          message: '数据返回失败!'
        })
        }
      })
    },
    thumbup(item){
      if(this.sceneDict[item.id].have_fav === true){
        if(this.sceneDict[item.id].fav_num > 0){
          this.sceneDict[item.id].fav_num -= 1
        }
        this.sceneDict[item.id].have_fav = false
      }
      else{
        this.sceneDict[item.id].fav_num += 1
        this.sceneDict[item.id].have_fav = true
      }
      thumbup(item.id)
    }
  },
  created() {
    // this.handleQuery()
    // this.templist()
    this.gettimelist()
    this.getScene()
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
.sceneSearch{
  width: 360px;
  height: 32px;
  background: #F2F4F7;
  border-radius: 4px;
}
.word {
  z-index: 53;
  position: absolute;
  left: 10px;
  top: 6px;
  width: 28px;
  display: block;
  overflow-wrap: break-word;
  color: rgba(255, 255, 255, 1);
  font-size: 14px;
  font-family: MicrosoftYaHei;
  white-space: nowrap;
  line-height: 14px;
}
.main {
  z-index: 52;
  width: 70px;
  height: 24px;
  margin-top: 20px;
  border-radius: 12px 0 0 12px;
  background-color: rgba(250, 63, 63, 1);
}
</style>
