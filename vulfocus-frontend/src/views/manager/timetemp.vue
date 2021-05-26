<template>
  <div style="width: 50%">
    <el-form label-width="170px" style="margin-left:0px" v-loading="loading" :model="data" element-loading-text="创建中">
      <el-form-item label="计时时间" :label-width="formLabelWidth">
        <el-input v-model="form.time_range" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item label="模版描述" :label-width="formLabelWidth">
        <el-input type="textarea" v-model="form.desc" autocomplete="off"></el-input>
      </el-form-item>
      <el-form-item>
      <el-button type="primary" @click="handleCreate()">创建模版</el-button>
      </el-form-item>
    </el-form>
    <el-table
      :data="tableData"
      style="width: 100%;margin:100 auto;margin-top:10px;">
      <el-table-column
        prop="temp_id"
        label="id"
        width="180">
      </el-table-column>
      <el-table-column
        prop="time_range"
        label="时间范围"
        width="180">
      </el-table-column>
      <el-table-column
        prop="time_desc"
        label="描述">
      </el-table-column>
      <el-table-column
      fixed="right"
      label="操作"
      width="100">
        <template slot-scope="{row}">
          <el-button type="text" size="small" @click='handleDelete(row)'>删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>


<script>
  import { timetemplist,timetempadd,timetempdelete } from '@/api/timemoudel'

  export default {
    inject:['reload'],
    data() {
      return {
        formLabelWidth:"100px",
        tableData: [],
        loading: false,
        form: {
          time_range:'',
          desc: '',
        },
      };
    },
    created(){
      this.templist()
    },
    methods: {
      templist(){
        timetemplist().then(response =>{
          let data = response.data.results
          console.log(data)
          this.tableData = data
          })
       },
      handleCreate(){
        timetempadd(this.form).then(response => {
          let rsDta = response.data
          if (rsDta.status === 200){
            this.$message({
              type: 'success',
              message: '创建成功'
            })
          }else{
            this.$message({
            type: 'error',
            message: rsDta.message,
          })
          }
          this.reload()
        })
      },
      handleDelete(row){
        timetempdelete(row.temp_id).then(response => {
          let data = response.data
          if (data.code === 200){
            this.$message({
              type:'success',
              message: data.message
            })
          }else{
            this.$message({
              type:'error',
              message: data.message
            })
          }
          this.reload()
        })
      }
    }
  }
</script>

<style scoped>
.el-row {
  display: flex;
  flex-wrap: wrap;
}
</style>
