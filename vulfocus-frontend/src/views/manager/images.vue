<template>
  <div class="app-container">
    <div class="filter-container">
      <el-autocomplete style="width: 30%"  v-model="searchImageName" size="medium" placeholder="镜像名称"
                       :fetch-suggestions="querySearchImageAsync" @select="handleImageSelect"></el-autocomplete>
      <el-button class="filter-item" size="medium" style="margin-left: 10px;margin-bottom: 10px" type="primary" icon="el-icon-search" @click="handleContainer(1)">
        查询
      </el-button>
    </div>
    <el-table
      :data="tableData" border stripe style="width: 100%" v-loading="loading">
      <el-table-column type="index" width="50"></el-table-column>
      <el-table-column prop="vul_name" width="150" :show-overflow-tooltip=true label="漏洞名称"></el-table-column>
      <el-table-column :show-overflow-tooltip=true prop="user_name" width="100" label="用户名"></el-table-column>
      <el-table-column prop="vul_host" width="200" :show-overflow-tooltip=true label="访问地址"></el-table-column>
      <el-table-column label="状态" width="85">
        <template slot-scope="{row}">
          <el-tag>{{row.container_status}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="vul_desc" :show-overflow-tooltip=true width="300" label="漏洞描述"></el-table-column>
      <el-table-column prop="combination_desc" label="操作" :show-overflow-tooltip=true>
        <template slot-scope="{row}">
          <el-button size="mini" type="primary" icon="el-icon-caret-left" v-if="row.container_status === 'stop'"
                     @click="startContainer(row)" >启动</el-button>
          <el-button size="mini" type="primary" icon="el-icon-loading" v-if="row.container_status === 'running'"
                     @click="stopContainer(row)" >停止</el-button>
          <el-button size="mini" type="danger" icon="el-icon-delete" v-if="row.container_status === 'running' || row.container_status === 'stop' && row.vul_host!==''"
                     @click="delContainer(row)" >删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 20px">
      <el-pagination
        :page-size="page.size"
        @current-change="initTable"
        layout="total, prev, pager, next, jumper"
        :total="page.total">
      </el-pagination>
    </div>
  </div>
</template>

<script>
  import { ImgList } from "@/api/docker"
  import { containerList,containerStop,containerStart,containerDel } from '@/api/container'
  import { getTask } from '@/api/tasks'
  import CountDown from 'vue2-countdown'
  export default {
    name: 'image',
    data(){
      return {
        page:{
          total: 0,
          size: 20,
        },
        searchImageId: null,
        searchImageName: null,
        imageList: [],
        tableData: [],
        loading:false,
      }
    },
    components: {
      CountDown
    },
    created(){
      this.initTable(1)
    },
    methods:{
      initTable(page){
        this.search("", page)
      },
      stopContainer(row){
        containerStop(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpStopContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpStopContainerInterval)
                  if(responseStatus === 200){
                    this.$message({
                      type: "success",
                      message: "删除成功"
                    });
                    this.initTable()
                  }else{
                    this.$message({
                      type: "error",
                      message: responseData["msg"]
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      },
      startContainer(row){
        containerStart(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpRunContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpRunContainerInterval)
                  if(responseStatus === 200){
                    this.$message({
                      type: "success",
                      message: "启动成功"
                    });
                    this.initTable()
                  }else{
                    this.$message({
                      type: "error",
                      message: responseData["msg"]
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      },
      delContainer(row){
        containerDel(row.container_id).then(response => {
          let taskId = response.data["data"]
          let tmpDeleteContainerInterval = window.setInterval(() => {
            setTimeout(()=>{
              getTask(taskId).then(response=>{
                let responseStatus = response.data["status"]
                let responseData = response.data
                if (responseStatus === 1001){
                  // 一直轮训
                }else{
                  clearInterval(tmpDeleteContainerInterval)
                  if (responseStatus === 200) {
                    this.$message({
                      type: 'success',
                      message: '删除成功'
                    });
                    this.initTable()
                  }else{
                    this.$message({
                      message: responseData["msg"],
                      type: "error",
                    })
                  }
                }
              })
            },1)
          },1000)
        })
      },
      querySearchImageAsync(queryString, cb) {
        this.imageList = []
        //this.searchImageName = null
        this.searchImageId = null
        if(queryString !== "" && queryString !== null && queryString.length !== 0){
          ImgList(queryString, true, 1).then(response => {
            let results = response.data.results
            if(results !== null){
              results.forEach((item, index, arr) => {
                this.imageList.push({"value": item["image_name"], "id": item["image_id"]})
              });
            }
            if(this.imageList.length > 0){
              cb(this.imageList);
            }
          })
        }
      },
      handleImageSelect(item){
        this.searchImageId = item.id
        this.searchImageName = item.value
      },
      handleContainer(page){
        let id = this.searchImageId
        this.search(id, page)
      },
      search(id,page){
        containerList('list', page, id).then(response => {
          this.tableData = response.data.results
          this.loading = false
          this.page.total = response.data.count
        })
      },
    }
  }
</script>

<style scoped>
</style>
