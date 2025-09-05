package com.example.test;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
public class TestActivityWithExistingInitViews extends AppCompatActivity {
    TextView existingText;
    Button newButton;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);
        // 现有的initViews调用
        initViews();
    
        initListener();}
    protected void initViews() {
        // 现有的代码
        existingText = findViewById(R.id.existing_text);
        existingText.setText("Existing text");
        // 初始化View绑定 - 替换@BindView注解
        existingText = findViewById(R.id.existing_text);
        newButton = findViewById(R.id.new_button);
    }
    public void onNewButtonClick() {
        // 点击事件
    }

    public void initListener() {
        // 初始化点击事件 - 替换@OnClick注解
        findViewById(R.id.new_button).setOnClickListener(v -> onNewButtonClick());
    }
}