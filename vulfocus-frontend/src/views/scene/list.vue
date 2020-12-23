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
            <img :src="item.image_name"  alt="" width="285px" height="300px;"/>
            <div class="container-title" style="margin-top: 5px;">
              <span>{{item.layout_name}}</span>
            </div>
            <div class="bottom clearfix" style="margin-top: 10px;height: 80px;">
              <span style="color:#999;font-size: 13px;" class="hoveDesc"> {{ item.layout_desc }}</span>
            </div>
            <el-row style="margin-top: 5px;margin-bottom: 10px; float: right">
              <el-button type="primary" size="mini" @click="handleInto(item)">进入</el-button>
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

export default {
  name: 'index',
  data(){
    return {
      tableData: [],
      search: "",
      page:{
        total: 0,
        size: 20,
      },
      // isAdmin: false
    }
  },
  methods: {
    layoutList(page){
      this.tableData = []
      layoutList(this.search, page, "flag").then(response => {
        let rsp = response.data
        rsp.results.forEach((info,index) => {
          info.image_name = process.env.VUE_APP_BASE_API+ '/static/'+ info.image_name
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
    handleQuery(){
      this.layoutList(1)
    },
    handleInto(item){
      this.$router.push({path: "/scene/index", query: {"layout_id": item.layout_id}})
    }
  },
  created() {
    this.handleQuery()
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
}
</style>
