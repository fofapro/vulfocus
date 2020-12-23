<template>
<div class="app-container">
  <el-row>
    <el-col :span="11">
      <el-card v-loading="loadingFlag" :element-loading-text="loadingText">
        <div slot="header" class="clearfix">
          <span>场景信息</span>
          <el-tooltip v-if="!isRun" content="运行中">
            <i style="color: #20a0ff;" class="el-icon-loading"></i>
          </el-tooltip>
          <el-tooltip v-if="isRun" content="未启动">
            <i class="fa fa-stop" aria-hidden="true"></i>
          </el-tooltip>
        </div>
        <div>
          <div class="text item">
            环境名称：{{layout.name}}
          </div>
          <div class="text item">
            环境描述：{{layout.desc}}
          </div>
          <div class="text item" >
            访问地址：
            <p v-for="(item,i) in open" >
              {{item}}
            </p>
          </div>
          <div class="text item">
            当前分数：{{currentScore}}
          </div>
          <div class="text item">
            当前进度：{{currentProgress}}
          </div>
          <div class="text item">
            当前排名：
            <span v-if="currentRank === 0" >
              未上榜
            </span>
            <span v-else-if="currentRank > 0" >
              {{currentRank}}
            </span>
          </div>
          <el-form >
            <el-form-item label="Flag">
              <el-input :disabled="isRun" size="small" style="width: 80%" v-model="flag" placeholder="请输入Flag：格式flag-{xxxxxxxx}"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button size="small" :disabled="isRun" type="primary" @click="handleFlag">提交</el-button>
              <el-button v-if="isAdmin===true && isRun" size="small" @click="handleRun" type="primary">启动</el-button>
              <el-button v-if="isAdmin===true && !isRun" size="small" @click="handleStop" type="primary">停止</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </el-col>
    <el-col :span="12" :offset="1">
      <el-card>
        <div slot="header" class="clearfix">
          <span>排名</span>
        </div>
        <div>
          <el-table :data="rankList">
            <el-table-column label="序号" type="index" :index="computeTableIndex" width="50"></el-table-column>
            <el-table-column prop="username" :show-overflow-tooltip=true label="用户名"></el-table-column>
            <el-table-column prop="score" label="积分" width="180"></el-table-column>
          </el-table>
        </div>
        <div style="margin-top: 20px">
          <el-pagination
            :page-size="page.size"
            @current-change="handleRank"
            layout="total, prev, pager, next, jumper"
            :total="page.total">
          </el-pagination>
        </div>
      </el-card>
    </el-col>
  </el-row>
  <div>

  </div>
</div>
</template>

<script>

import { mapGetters } from 'vuex'
import {sceneGet, sceneStart, sceneStop,sceneFlag, sceneRank} from '@/api/scene'

export default {
  name: 'index.vue',
  data(){
    return {
      layout: {
        id: "",
        name: "",
        desc: "",
      },
      loadingFlag: true,
      loadingText: "环境启动中",
      flag: "",
      isAdmin: false,
      page:{
        total: 0,
        size: 20,
        page: 1
      },
      isRun: false,
      currentProgress: "",
      currentRank: 0,
      currentScore: 0,
      open: [],
      rankList:[]
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
    if (this.roles.length >0 &&this.roles[0] === "admin"){
      this.isAdmin = true
    }
    this.initModelInfo()
    this.handleRank(1)
  },
  methods:{
    /**
     * 初始化模式信息
     */
    initModelInfo(){
      this.loadingText = "模式信息初始化中"
      this.loadingFlag = true
      // 环境 id
      let layoutId = this.$route.query.layout_id
      if (layoutId === undefined || layoutId == null || layoutId === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      this.layout.id = layoutId
      sceneGet(layoutId).then(response=>{
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        let msg = rsp.msg
        if (status === 200){
          this.layout.name = rsp.data["layout"]["name"]
          this.layout.desc = rsp.data["layout"]["desc"]
          this.open = rsp.data["open"]
          if(!rsp.data["is_run"]){
            this.isRun = true
          }
        }else{
          this.$message({
            message: msg,
            type: "error",
          })
        }
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      })
    },
    /**
     * 启动
     */
    handleRun(){
      this.loadingFlag = true
      this.loadingText= "模式启动中"
      let layoutId = this.layout.id
      if (layoutId === undefined || layoutId == null || layoutId === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      sceneStart(layoutId).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        let msg = rsp.msg
        if (status === 200){
          this.layout.name = rsp.data["layout"]["name"]
          this.layout.desc = rsp.data["layout"]["desc"]
          this.open = rsp.data["open"]
          if (undefined === rsp.data["is_run"]){
            rsp.data["is_run"] = true
          }
          this.isRun = !rsp.data["is_run"]
          console.log(this.isRun)
          this.$message({
            message: "启动成功",
            type: 'success'
          })
        }else{
          this.$message({
            message: msg,
            type: "error",
          })
        }
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      })
    },
    /**
     * 停止
     */
    handleStop(){
      this.loadingFlag = true
      this.loadingText = "模式停止中"
      let layoutId = this.layout.id
      if (layoutId === undefined || layoutId == null || layoutId === ""){
        this.$message({
          message: "参数不能为空",
          type: "error",
        })
        this.$router.push({path: "/scene/list"})
      }
      sceneStop(layoutId).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        let msg = rsp.msg
        if (status === 200){
          this.$message({
            message: "关闭成功",
            type: 'success'
          })
          this.initModelInfo()
        }else{
          this.$message({
            message: msg,
            type: "error",
          })
        }
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
      })
      // this.loadingFlag = false
    },
    /**
     * 提交flag
     */
    handleFlag(){
      let flag = this.flag
      this.loadingFlag = true
      this.loadingText = "Flag 提交中"
      if (flag === "" || flag === null){
        this.$message({
          message: "flag 不能为空",
          type: "error"
        })
        return
      }
      sceneFlag(this.layout.id, flag).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        let status = rsp.status
        if (status === 200){
          this.$message({
            message:  "恭喜！通过",
            type: "success",
          })
          this.flag = ""
          this.handleRank(1)
        }else{
          this.$message({
            message:rsp.msg,
            type: "error"
          })
        }
      }).catch(err =>{
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: "error",
        })
      })
    },
    /**
     * 初始化排行
     */
    handleRank(page){
      this.loadingFlag = true
      this.loadingText = "排行初始化中"
      this.page.page = page
      sceneRank(this.layout.id, page).then(response => {
        this.loadingFlag = false
        let rsp = response.data
        this.page.total = rsp.count
        this.rankList = rsp.result
        // 当前进度
        this.currentProgress = rsp.progress
        // 当前排名
        this.currentRank = rsp.current
        // 当前分数
        this.currentScore = rsp.score
      }).catch(err => {
        this.loadingFlag = false
        this.$message({
          message: "服务器内部错误",
          type: 'error'
        })
      })
    },
    computeTableIndex(index){
      return (this.page.page - 1) * this.page.size + index + 1
    }
  }
}
</script>

<style scoped>
.text {
  font-size: 14px;
}

.item {
  margin-bottom: 18px;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
</style>
