import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from dotenv import load_dotenv
import os
from report_generator import create_pdf_report

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")




st.set_page_config(
    page_title="AI-Powered HR Analytics Dashboard",
    page_icon="💼",
    layout="wide"
)

if "gemini_findings" not in st.session_state:
    st.session_state.gemini_findings = ""

if "gemini_recommendations" not in st.session_state:
    st.session_state.gemini_recommendations = ""

if "gemini_risk" not in st.session_state:
    st.session_state.gemini_risk = ""

if "gemini_summary" not in st.session_state:
    st.session_state.gemini_summary = ""



st.title("💼 AI-Powered HR Analytics Dashboard")
st.info("""
    Upload an HR dataset to generate
    KPI metrics, visual analytics,
    risk assessment, AI findings,
    recommendations, and executive reports.
    """)
st.write("Upload your HR dataset below")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["CSV"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    filtered_df = df.copy()

    st.sidebar.title("🎛 Dashboard Filters")
    st.sidebar.divider()

    # Sidebar Department Filter
    department_options = ["All"] + sorted(
        df["Department"].unique().tolist()
    )

    selected_department = st.sidebar.selectbox(
        "Select Department",
        department_options
    )

    # Apply filter
    if selected_department != "All":
        filtered_df= filtered_df[filtered_df["Department"] == selected_department]
    
    # Gender Filter
    gender_options = ["All"] + sorted(
        df["Gender"].unique().tolist()
        )

    selected_gender = st.sidebar.selectbox(
        "Select Gender",
        gender_options
        )

    if selected_gender != "All":
        filtered_df=filtered_df[filtered_df["Gender"] == selected_gender]
    
    # Job Role Filter
    job_role_options = ["All"] + sorted(
         df["JobRole"].unique().tolist()
    )
    selected_job_role = st.sidebar.selectbox(
        "Select Job Role",
        job_role_options
    )
    if selected_job_role != "All":
        filtered_df=filtered_df[filtered_df["JobRole"] == selected_job_role]

    # Marital Status Filter
    marital_options = ["All"] + sorted(
        df["MaritalStatus"].unique().tolist()
    )
    selected_marital = st.sidebar.selectbox(
        "Select Marital Status",
        marital_options
    )
    if selected_marital != "All":
        filtered_df = filtered_df[filtered_df["MaritalStatus"] == selected_marital]

    #Education Filter
    education_options = ["All"] + sorted(
        df["EducationField"].unique().tolist()
    )
    selected_education = st.sidebar.selectbox(
        "Select Education Field",
        education_options
    )
    if selected_education != "All":
        filtered_df = filtered_df[filtered_df["EducationField"]==selected_education]
    if filtered_df.empty:
        st.warning(
            "No data available for selected filters"
        )
        st.stop()

    # Dataset Information
    rows = filtered_df.shape[0]
    cols = filtered_df.shape[1]
    missing_values = filtered_df.isnull().sum().sum()

    col1,col2,col3 = st.columns(3)

    col1.metric(f"Rows ",rows)
    col2.metric(f"Columns ",cols)
    col3.metric(f"Missing Values ",missing_values)

    st.info("Dataset Preview")
    st.dataframe(
        filtered_df.head(),
        use_container_width=True
        )

    #HR KPI Calculations

    total_emp = len(filtered_df)
    attrition_count = len(filtered_df[filtered_df["Attrition"]=="Yes"])
    if total_emp > 0:
        attrition_rate = round(
        (attrition_count / total_emp) * 100,
        2
    )
    else:
        attrition_rate = 0
    average_age = round(filtered_df["Age"].mean(),1)
    average_income = round(filtered_df["MonthlyIncome"].mean(),0)

   

    # Shared Analytics Calculations
    attrition_dept_data = (
        filtered_df[filtered_df["Attrition"] == "Yes"]
        .groupby("Department")
        .size()
    )
    if not attrition_dept_data.empty:
        highest_attrition_dept = attrition_dept_data.idxmax()
    else:
        highest_attrition_dept = "No Attrition Found"
    
    overtime_yes_rate = (
        filtered_df[filtered_df["OverTime"]=="Yes"]["Attrition"]
        .eq("Yes")
        .mean()*100
    )
    overtime_no_rate = (
        filtered_df[filtered_df["OverTime"] == "No"]["Attrition"]
        .eq("Yes")
        .mean()*100
    )

    st.divider()
    if "show_insights" not in st.session_state:
        st.session_state.show_insights = False

    if st.button("Generate HR Insights"):
        st.session_state.show_insights = True

    if st.session_state.show_insights:
        st.success("HR Insights Module Activated!")
        st.subheader("HR KPI Dashboard")

        with st.container(border=True):
            col4, col5, col6, col7 = st.columns(4)
            col4.metric("Total Employees", total_emp)
            col5.metric("Attrition Rate", attrition_rate)
            col6.metric("Average Age", average_age)
            col7.metric("Average Income", f"${average_income:,.0f}")
        
        st.caption(
            """
            KPIs automatically update based on
            selected department, gender,
            and job role filters.
            """
        )

        tab1,tab2,tab3,tab4,tab5 = st.tabs(
            [
                "📊 Charts   ",
                "   📈 Analytics Findings   ",
                "   💡 Analytics Recommendations   ",
                "   ⚠ Risk Dashboard   ",
                "   📋 Executive Summary   "
            ]
        )
        with tab1:
            # Department Charts
            show_department_charts = (
                selected_department == "All"
                and selected_job_role == "All"
            )
            if show_department_charts:
                st.subheader("Attrition by Department")
                dept_attrition = (
                filtered_df[filtered_df["Attrition"] == "Yes"]
                .groupby("Department")
                .size()
                .reset_index(name="Attrition Count")
             )

                fig_deptArr = px.bar(
                dept_attrition,
                x="Department",
                y="Attrition Count",
                title="Employees Leaving by Department"
                )
                st.plotly_chart(fig_deptArr,use_container_width=True)

                st.subheader("Attrition Rate by Department(%)")

                dept_summary =(
                filtered_df.groupby("Department")["Attrition"]
                .apply(lambda x:(x=="Yes").mean()*100)
                .reset_index(name="Attrition Rate")
                )

                fig_rate_dept = px.bar(
                dept_summary,
                x="Department",
                y="Attrition Rate",
                title="Attrition Rate by Department(%)",
                text_auto=".2f"
                )

                st.plotly_chart(fig_rate_dept,use_container_width=True)
            elif selected_department != "All":
                st.info(
                "Department charts hidden because filters affect department comparison."
                )
        
            if selected_gender == "All":
                st.subheader("Attrition by Gender")
                gender_attrition = (
                filtered_df[filtered_df["Attrition"]=="Yes"]
                .groupby("Gender")
                .size()
                .reset_index(name="Attrition Count")
                )
                fig_genderArr = px.pie(
                gender_attrition,
                names="Gender",
                values="Attrition Count",
                title="Attrition Distribution by Gender"
                )
                st.plotly_chart(fig_genderArr, use_container_width=True)
            else:
                st.info("Gender chart hidden because a gender filter is selected.")
            
            st.subheader("Attrition by Overtime")
            overtime_attrition = (
                filtered_df[filtered_df["Attrition"] == "Yes"]
                .groupby("OverTime")
                .size()
                .reset_index(name="Attrition Count")
            )

            fig_OvertimeArr = px.pie(
                overtime_attrition,
                names="OverTime",
                values="Attrition Count",
                title="Attrition Count by OverTime"
            )
            st.plotly_chart(fig_OvertimeArr, use_container_width=True)

            st.subheader("Attrition Rate by Overtime(%)")

            overtime_summary =(
                filtered_df.groupby("OverTime")["Attrition"]
                .apply(lambda x:(x=="Yes").mean()*100)
                .reset_index(name="Attrition Rate")
            )

            fig_rate_overtime = px.pie(
                overtime_summary,
                names="OverTime",
                values="Attrition Rate",
                title="Attrition Rate by Overtime (%)",
                
            )

            st.plotly_chart(fig_rate_overtime,use_container_width=True)
            st.divider()
        
        with tab2:

            st.subheader("🤖 AI Findings")
            
            # Dynamic findings
            findings = []

            # Attrition findings
            if attrition_rate > 20:
                findings.append(
                    f"High employee attrition detected ({attrition_rate}%). Immediate retention actions are recommended."
                )
            elif attrition_rate > 10:
                findings.append(
                    f"Employee attrition is moderate ({attrition_rate}%) and should be monitored closely."
                )
            else:
                findings.append(
                    f"Employee attrition remains within acceptable limits ({attrition_rate}%)."
                )
            
            # Department findings
            findings.append(
                f"{highest_attrition_dept} records the highest employement attrition"
            )

            #Overtime findings
            if overtime_yes_rate > overtime_no_rate:
                findings.append(
                    "Employees working overtime exhibit higher turnover risk."
                )
            
            # Age finding
            if average_age < 35:
                findings.append(
                    f"Average employee age is {average_age} years, suggesting turnover among younger employees."
                    )

            else:
                findings.append(
                    f"Average employee age is {average_age} years, indicating turnover within a mid-career workforce."
                    )
            
            # Income Finding
            if average_income < 5000:
                findings.append(
                    "Average monthly income is relatively low and may influence employee retention."
                )

            else:
                findings.append(
                    f"Average monthly income is ${average_income:,.0f}, indicating competitive compensation levels."
                )
            
            #display findings
            for finding in findings:
                st.info(f"* {finding}")
            

            st.divider()

            st.divider()
            st.subheader("🤖 Gemini AI Analysis")
            if st.button("Generate AI Analysis"):
                prompt = f"""
                    You are an HR Analysis expert.
                    Analysis the followingg HR metrics and provide 5 professional business findings.
                    Total Employees: {total_emp}

                    Attrition Rate: {attrition_rate}%

                    Hihest Attrition Department: {highest_attrition_dept}

                    Average Age: {average_age}

                    Average Monthly Income: {average_income}

                    Overtime Attrition Rate: {overtime_yes_rate:.2f}%

                    Non-Overtime Attrition Rate : {overtime_no_rate:.2f}%

                    Provide:
                    1. Key Findings
                    2. Business Implications
                    3. Areas of concern

                    Keep response concise and professional

                    """
                response = model.generate_content(prompt)
                st.session_state.gemini_findings = response.text
            st.info(st.session_state.gemini_findings)

        with tab3:

            st.subheader("💡 AI Recommendations")
            recommendations = []
                
            # Attrition recommendation
            if attrition_rate > 20:
                recommendations.append(
                    "Implement an immediate employee retention program to address elevated attrition levels."
                )
            elif attrition_rate > 10:
                recommendations.append(
                    "Monitor workforce turnover trends and strengthen employee engagement initiatives."
                )
                
            # Overtime recommendation
            if overtime_yes_rate > overtime_no_rate:
                recommendations.append(
                    "Review overtime practices and workload distribution to reduce burnout risk."
                )
                
            # department recommendation
            if highest_attrition_dept != "No Attrition Found":
                recommendations.append(
                    f"Conduct a targeted retention review within the {highest_attrition_dept} department."
                )
                
            # Age recommendation
            if average_age < 35:
                recommendations.append(
                    "Enhance career growth opportunities for early-career employees."
                )
            else:
                recommendations.append(
                    "Strengthen leadership development and long-term retention strategies."
                )
                
            # General recommendation
            recommendations.append(
                    "Conduct periodic employee satisfaction surveys to identify emerging concerns."
                )

            #display recommendation
            for rec in recommendations:
                st.info(f"* {rec}")

            st.divider()
        

            st.divider()
            st.subheader("🤖 Gemini AI Recommendations")
            if st.button("Generate AI Recommendations"):
                prompt = f"""
                    You are a Senior HR Strategy Consultant.

                    Based on the following HR metrics:

                    Total Employees: {total_emp}

                    Attrition Rate: {attrition_rate}%

                    Highest Attrition Department:
                    {highest_attrition_dept}

                    Average Age:
                    {average_age}

                    Average Monthly Income:
                    {average_income}

                    Overtime Attrition Rate:
                    {overtime_yes_rate:.2f}%

                    Non-Overtime Attrition Rate:
                    {overtime_no_rate:.2f}%

                    Provide:

                    1. Strategic Recommendations
                    2. Retention Actions
                    3. Workforce Planning Suggestions
                    4. Leadership Recommendations

                    Give 5 concise recommendations.
                    """
                response = model.generate_content(prompt)
                st.session_state.gemini_recommendations = response.text
            st.markdown(st.session_state.gemini_recommendations)
                
        with tab4:

            st.subheader("⚠️ HR Risk Alerts")
            risks = []

            # Attrition risk
            if attrition_rate > 20:
                risks.append(
                    "High Attrition Risk"
                )
            elif attrition_rate > 10:
                risks.append(
                    "Moderate Attrition Risk"
                )
            
            # Overtime risk
            if overtime_yes_rate > overtime_no_rate:
                risks.append(
                    "Overtime Burnout Risk"
                )
            
            # Department risk
            if highest_attrition_dept != "No Attrition Found":
                risks.append(
                    f"{highest_attrition_dept} Retention Risk"
                )
            
            for risk in risks:
                st.warning(risk)

            st.divider()
            st.subheader("🤖 Gemini Risk Assessment")

            if st.button("Generate AI Risk Assessment"):
                prompt = f"""
                    You are a Senior HR Risk Consultant.

                    Analyze the following HR metrics and identify the most important workforce risks.

                    HR Metrics:

                    Total Employees: {total_emp}

                    Attrition Rate: {attrition_rate}%

                    Highest Attrition Department:
                    {highest_attrition_dept}

                    Average Age:
                    {average_age}

                    Average Monthly Income:
                    {average_income}

                    Overtime Attrition Rate:
                    {overtime_yes_rate:.2f}%

                    Non-Overtime Attrition Rate:
                    {overtime_no_rate:.2f}%

                    Provide:

                    1. Top Workforce Risks
                    2. Operational Risks
                    3. Talent Retention Risks
                    4. Future Business Risks

                    Use professional business language.

                    Limit response to 5 key risk points.
                """
                response = model.generate_content(prompt)
                st.session_state.gemini_risk = response.text
            st.markdown(st.session_state.gemini_risk)

        with tab5:

            st.subheader("📋 Executive Summary")

            # Attrition Narrative
            if attrition_rate > 20:
                attrition_text = "high"
            elif attrition_rate > 10:
                attrition_text = "moderate"
            else:
                attrition_text = "low"
                
            # Overtime Narrative
            if overtime_yes_rate > overtime_no_rate:
                overtime_text = (
                    "Employees working overtime demonstrate elevated attrition risk."
                )
            else:
                overtime_text = (
                    "Overtime does not appear to be a significant attrition driver."
                )
            
            # Age Narrative
            if average_age < 35:
                age_text = (
                    "Employee turnover appears concentrated among younger employees."
                 )
            else:
                age_text = (
                    "Employee turnover appears concentrated within a mid-career workforce."
                )

            # Build Summary
            summary = f"""
                            The organization currently exhibits a {attrition_text} attrition rate of {attrition_rate}%.

                        {highest_attrition_dept} records the highest employee turnover within the organization.

                        {overtime_text}

                        {age_text}

                        Management should prioritize employee retention initiatives, workforce engagement programs, and targeted department-level interventions to reduce future turnover.
                                """

            st.success(summary)

            st.divider()
            st.subheader("🤖 Gemini Executive Summary")

            if st.button("Generate AI Executive Summary"):
                prompt = f"""
                    You are a Chief HR Officer preparing a report
                    for senior management.

                    Analyze the following HR metrics:

                    Total Employees: {total_emp}

                    Attrition Rate: {attrition_rate}%

                    Highest Attrition Department:
                    {highest_attrition_dept}

                    Average Age:
                    {average_age}

                    Average Monthly Income:
                    {average_income}

                    Overtime Attrition Rate:
                    {overtime_yes_rate:.2f}%

                    Non-Overtime Attrition Rate:
                    {overtime_no_rate:.2f}%

                    Prepare:

                    1. Executive Summary
                    2. Business Impact
                    3. Key Risks
                    4. Strategic Priorities

                    Write in a professional executive-report style.

                    Limit response to 250 words   
                """
                response = model.generate_content(prompt)
                st.session_state.gemini_summary = response.text
            with st.container(border=True):
                st.markdown(st.session_state.gemini_summary)

        report_content = f"""
            HR KPI SUMMARY

            Total Employees: {total_emp}

            Attrition Rate: {attrition_rate}%

            Average Age: {average_age}

            Average Monthly Income: ${average_income:,.0f}


            ================================================== 
            GEMINI FINDINGS

            {st.session_state.get('gemini_findings','Not Generated')}


            ================================================== 
            GEMINI RECOMMENDATIONS

            {st.session_state.get('gemini_recommendations','Not Generated')}


            ==================================================
            GEMINI RISK ASSESSMENT

            {st.session_state.get('gemini_risk','Not Generated')}


            ==================================================
            GEMINI EXECUTIVE SUMMARY

            {st.session_state.get('gemini_summary','Not Generated')}
        
        """ 
        if st.session_state.gemini_summary == "":
            st.warning(
                 "Please generate Gemini Executive Summary before exporting."
                )  
        st.success(
            "Powered by Gemini AI"
            )    
        if st.button("📄 Generate PDF Report"):
           pdf_path = "outputs/HR_Report.pdf"

           create_pdf_report(
               pdf_path,
               report_content
           )

           st.success("AI Report Generated Successfully!")

           with open(pdf_path,"rb") as pdf_file:
               st.download_button(
                   label= "⬇ Download AI Report",
                   data = pdf_file,
                   file_name= "HR_Analytics_Report.pdf",
                   mime="Application/pdf"
               )
        
        # Footer
        st.divider()
        st.caption(
            "Developed using Python, Streamlit, Plotly and Gemini AI"
        )


            






       
    


